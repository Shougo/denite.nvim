# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import error, echo, debug, escape_syntax
from ..prompt.key import Key
from ..prompt.util import getchar
from .. import denite

import re
import traceback
import time


# Port 'isprint' function from curses.ascii which is missing in Windows.
# https://github.com/python/cpython/blob/3.5/Lib/curses/ascii.py#L62
def isprint(c):
    c = ord(c) if type(c) == type('') else c
    return c >= 32 and c <= 126


def _safe_isprint(c):
    if not c or c == '\0':
        return False
    return isprint(c)


class Default(object):

    def __init__(self, vim):
        self.__vim = vim
        self.__denite = denite.Denite(vim)
        self.__cursor = 0
        self.__win_cursor = 1
        self.__candidates = []
        self.__candidates_len = 0
        self.__result = []
        self.__context = {}
        self.__current_mode = ''
        self.__mode_stack = []
        self.__current_mappings = {}
        self.__input_before = ''
        self.__input_cursor = ''
        self.__input_after = ''
        self.__bufnr = -1
        self.__winid = -1
        self.__winrestcmd = ''
        self.__winsaveview = {}
        self.__initialized = False
        self.__winheight = 0
        self.__is_multi = False
        self.__matched_pattern = ''
        self.__statusline_sources = ''

    def start(self, sources, context):
        try:
            if self.__initialized and context['resume']:
                # Skip the initialization
                self.__current_mode = context['mode']

                self.init_buffer()
                self.change_mode(self.__current_mode)
                self.input_loop()
            else:
                self.__context = context
                self.__context['sources'] = sources
                self.__context['is_redraw'] = False
                self.__default_mappings = self.__vim.eval(
                    'g:denite#_default_mappings')
                self.__current_mode = context['mode']
                self.__is_multi = len(sources) > 1

                self.__denite.start(self.__context)
                self.__denite.on_init(self.__context)

                self.__denite.gather_candidates(self.__context)
                self.update_candidates()
                if self.check_empty():
                    return self.__result

                self.init_buffer()
                self.init_cursor()

                self.change_mode(self.__current_mode)

                self.__initialized = True

                self.input_loop()
        except Exception:
            for line in traceback.format_exc().splitlines():
                error(self.__vim, line)
            error(self.__vim,
                  'An error has occurred. Please execute :messages command.')
        return self.__result

    def init_buffer(self):
        self.__winheight = int(self.__context['winheight'])
        self.__prev_winid = self.__vim.call('win_getid')
        self.__prev_bufnr = self.__vim.current.buffer.number
        self.__prev_tabpages = self.__vim.call('tabpagebuflist')
        self.__winrestcmd = self.__vim.call('winrestcmd')
        self.__winsaveview = self.__vim.call('winsaveview')

        if self.__winid > 0 and self.__vim.call(
                'win_gotoid', self.__winid):
            # Move the window to bottom
            self.__vim.command('wincmd J')
        else:
            # Create new buffer
            self.__vim.command('silent botright new denite')
        self.__vim.command('resize ' + str(self.__winheight))
        self.__vim.command('nnoremap <silent><buffer> <CR> ' +
                           ':<C-u>Denite -resume -buffer_name=' +
                           self.__context['buffer_name'] + '<CR>')

        self.__options = self.__vim.current.buffer.options
        self.__options['buftype'] = 'nofile'
        self.__options['filetype'] = 'denite'
        self.__options['swapfile'] = False
        self.__options['modifiable'] = True

        self.__window_options = self.__vim.current.window.options
        if self.__context['cursorline']:
            self.__window_options['cursorline'] = True
        self.__window_options['colorcolumn'] = ''
        self.__window_options['number'] = False
        self.__window_options['relativenumber'] = False
        self.__window_options['foldenable'] = False
        self.__window_options['foldcolumn'] = 0

        self.__bufvars = self.__vim.current.buffer.vars
        self.__bufnr = self.__vim.current.buffer.number
        self.__winid = self.__vim.call('win_getid')

        self.__bufvars['denite_statusline_mode'] = ''
        self.__bufvars['denite_statusline_sources'] = ''
        self.__bufvars['denite_statusline_path'] = ''
        self.__bufvars['denite_statusline_linenr'] = ''

        self.__init_syntax()

        if self.__context['statusline']:
            self.__window_options['statusline'] = (
                '%#deniteMode#%{denite#get_status_mode()}%* ' +
                '%{denite#get_status_sources()} %=' +
                '%#deniteStatusLinePath# %{denite#get_status_path()} %*' +
                '%#deniteStatusLineNumber#%{denite#get_status_linenr()}%*')

    def __init_syntax(self):
        self.__vim.command('syntax case ignore')
        self.__vim.command('highlight default link ' +
                           self.__context['cursor_highlight'] + ' Normal')
        self.__vim.command('highlight default link deniteMode ModeMsg')
        self.__vim.command('highlight default link deniteMatched Search')
        self.__vim.command('highlight default link ' +
                           'deniteStatusLinePath Comment')
        self.__vim.command('highlight default link ' +
                           'deniteStatusLineNumber LineNR')

        for source in [x for x in self.__denite.get_current_sources()]:
            name = source.name.replace('/', '_')

            self.__vim.command(
                'highlight default link ' +
                'deniteSourceLine_' + name +
                ' Type'
            )

            syntax_line = 'syntax match %s /^%s/ nextgroup=%s keepend' % (
                'deniteSourceLine_' + name,
                escape_syntax(source.name if self.__is_multi else ''),
                source.syntax_name,
            )
            self.__vim.command(syntax_line)
            source.highlight_syntax()

    def init_cursor(self):
        self.__cursor = 0
        self.__win_cursor = 1

    def update_buffer(self):
        max = len(str(self.__candidates_len))
        linenr = ('{:'+str(max)+'}/{:'+str(max)+'}').format(
            self.__cursor + self.__win_cursor,
            self.__candidates_len)
        mode = '-- ' + self.__current_mode.upper() + ' -- '
        self.__bufvars['denite_statusline_mode'] = mode
        self.__bufvars['denite_statusline_sources'] = self.__statusline_sources
        self.__bufvars['denite_statusline_path'] = (
            '[' + self.__context['path'] + ']')
        self.__bufvars['denite_statusline_linenr'] = linenr

        self.__vim.command('silent! syntax clear deniteMatched')
        if self.__matched_pattern != '':
            self.__vim.command(
                'silent! syntax match deniteMatched /' +
                escape_syntax(self.__matched_pattern) + '/ contained')

        del self.__vim.current.buffer[:]
        self.__vim.current.buffer.append(
            ['%s %s' % (
                x['source'] if self.__is_multi else '',
                x.get('abbr', x['word']))
             for x in self.__candidates[self.__cursor:
                                        self.__cursor + self.__winheight]])
        del self.__vim.current.buffer[0]

        self.__options['modified'] = False

        self.move_cursor()

    def check_empty(self):
        return not (self.__context['empty'] or
                    self.__denite.is_async() or self.__candidates)

    def update_candidates(self):
        pattern = ''
        sources = ''
        self.__candidates = []
        for name, all, candidates in self.__denite.filter_candidates(
                self.__context):
            self.__candidates += candidates
            sources += '{}({}/{}) '.format(name, len(candidates), len(all))

            matchers = self.__denite.get_source(name).matchers
            for filter in [self.__denite.get_filter(x) for x in matchers
                           if self.__denite.get_filter(x)]:
                pat = filter.convert_pattern(self.__context['input'])
                if pat != '':
                    pattern = pat
                    break
        self.__matched_pattern = pattern
        self.__candidates_len = len(self.__candidates)

        if self.__denite.is_async():
            sources = '[async] ' + sources
        self.__statusline_sources = sources

    def move_cursor(self):
        self.__vim.call('cursor', [self.__win_cursor, 1])
        self.__vim.call('clearmatches')
        self.__vim.call('matchaddpos',
                        self.__context['cursor_highlight'],
                        [[self.__win_cursor, 1]])
        if self.__context['auto_preview']:
            self.do_action(self.__context, 'preview')

    def change_mode(self, mode):
        custom = self.__context['custom']['map']

        self.__current_mode = mode

        raw_mappings = self.__default_mappings['_'].copy()
        if '_' in custom:
            raw_mappings.update(custom['_'])

        if mode in self.__default_mappings:
            raw_mappings.update(self.__default_mappings[mode])
        if mode in custom:
            raw_mappings.update(custom[mode])

        self.__current_mappings = {
            Key.parse(self.__vim, k).code: v
            for k, v in raw_mappings.items()
        }
        self.update_buffer()

    def quit_buffer(self):
        self.__vim.command('redraw | echo')
        self.__vim.command('pclose!')

        if not self.__vim.call('bufloaded', self.__bufnr):
            return

        # Restore the view
        self.__vim.call('win_gotoid', self.__prev_winid)
        self.__vim.command('silent bdelete! ' + str(self.__bufnr))

        if self.__vim.call('tabpagebuflist') == self.__prev_tabpages:
            self.__vim.command(self.__winrestcmd)

        # Note: Does not work for line source
        # if self.__vim.current.buffer.number == self.__prev_bufnr:
        #     self.__vim.call('winrestview', self.__winsaveview)

    def update_prompt(self):
        self.__vim.command('redraw')
        if self.__context['prompt'] != '':
            echo(self.__vim, self.__context['prompt_highlight'],
                 self.__context['prompt'] + ' ')
        echo(self.__vim, 'Normal',
             self.__input_before)
        echo(self.__vim, self.__context['cursor_highlight'],
             self.__input_cursor)
        echo(self.__vim, 'Normal',
             self.__input_after)

    def update_input(self):
        self.__context['input'] = self.__input_before
        self.__context['input'] += self.__input_cursor
        self.__context['input'] += self.__input_after
        self.update_candidates()
        self.update_buffer()
        self.update_prompt()
        self.init_cursor()

    def redraw(self):
        self.__context['is_redraw'] = True
        self.__denite.gather_candidates(self.__context)
        self.update_candidates()
        self.update_buffer()
        self.__context['is_redraw'] = False

    def debug(self, expr):
        debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', '[denite]' + str(msg))

    def input_loop(self):
        self.__input_before = self.__context['input']
        self.__input_cursor = ''
        self.__input_after = ''

        while True:
            self.update_prompt()

            is_async = self.__denite.is_async()
            if is_async:
                time.sleep(0.005)
                key = Key.parse(self.__vim, getchar(self.__vim, 0))
            else:
                key = Key.parse(self.__vim, getchar(self.__vim))

            # Terminate input_loop when user hit <C-c>
            if key.code == 0x03:
                self.quit()
                break

            mapping = self.__current_mappings.get(key.code, None)
            if mapping:
                map_args = re.split(':', mapping)
                arg = ':'.join(map_args[1:])
                if hasattr(self, map_args[0]):
                    func = getattr(self, map_args[0])
                    ret = func() if len(map_args) == 1 else func(arg)
                    if ret:
                        break
                    continue
            elif (self.__current_mode == 'insert' and _safe_isprint(key.char)):
                # Normal input string
                self.__input_before += key.char
                self.update_input()
                continue

            if is_async:
                self.update_candidates()
                self.update_buffer()
                if self.check_empty():
                    self.quit()
                    break

    def quit(self):
        self.__denite.on_close(self.__context)
        self.quit_buffer()
        self.__result = []
        return True

    def do_action(self, action):
        if self.__cursor >= self.__candidates_len:
            return

        candidate = self.__candidates[self.__cursor + self.__win_cursor - 1]
        if 'kind' in candidate:
            kind = candidate['kind']
        else:
            kind = self.__denite.get_source(candidate['source']).kind

        prev_id = self.__vim.call('win_getid')
        self.__vim.call('win_gotoid', self.__prev_winid)
        now_id = self.__vim.call('win_getid')
        if prev_id == now_id:
            # The previous window search is failed.
            # Jump to the other window.
            if len(self.__vim.windows) == 1:
                self.__vim.command('topleft new')
            else:
                self.__vim.command('wincmd w')
        try:
            is_quit = not self.__denite.do_action(
                self.__context, kind, action, [candidate])
        except Exception:
            for line in traceback.format_exc().splitlines():
                error(self.__vim, line)
            error(self.__vim,
                  'The action ' + action + ' execution is failed.')
            return
        self.__vim.call('win_gotoid', prev_id)

        if is_quit:
            self.__denite.on_close(self.__context)
            if self.__context['quit']:
                self.quit_buffer()
            else:
                # Disable quit flag
                is_quit = False
        self.__result = [candidate]
        return is_quit

    def delete_backward_char(self):
        self.__input_before = re.sub('.$', '', self.__input_before)
        self.update_input()

    def delete_backward_word(self):
        self.__input_before = re.sub('[^/ ]*.$', '', self.__input_before)
        self.update_input()

    def delete_backward_line(self):
        self.__input_before = ''
        self.update_input()

    def paste_from_register(self):
        self.__input_before += re.sub(r'\n', '', self.__vim.eval('@"'))
        self.update_input()

    def move_to_next_line(self):
        if (self.__win_cursor < self.__candidates_len and
                self.__win_cursor < self.__winheight):
            self.__win_cursor += 1
        elif self.__win_cursor + self.__cursor < self.__candidates_len:
            self.__cursor += 1
        else:
            return
        self.update_buffer()

    def move_to_prev_line(self):
        if self.__win_cursor > 1:
            self.__win_cursor -= 1
        elif self.__cursor >= 1:
            self.__cursor -= 1
        else:
            return
        self.update_buffer()

    def input_command_line(self):
        self.__vim.command('redraw')
        input = self.__vim.call(
            'input', self.__context['prompt'] + ' ',
            self.__context['input'])
        self.__input_before = input
        self.__input_cursor = ''
        self.__input_after = ''
        self.update_input()

    def enter_mode(self, mode):
        self.__mode_stack.append(self.__current_mode)
        self.change_mode(mode)

    def leave_mode(self):
        if not self.__mode_stack:
            return self.quit()

        self.__current_mode = self.__mode_stack[-1]
        self.__mode_stack = self.__mode_stack[:-1]
        self.change_mode(self.__current_mode)

    def suspend(self):
        self.__options['modifiable'] = False
        return True
