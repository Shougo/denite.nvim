# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import error, echo, debug
from .. import denite

import re
import traceback
import time


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
        self.__initialized = False
        self.__winheight = 0

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

                self.__denite.start(self.__context)
                self.__denite.on_init(self.__context)

                self.init_buffer()
                self.init_cursor()
                self.__initialized = True

                self.__denite.gather_candidates(self.__context)
                self.change_mode(self.__current_mode)

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

        if self.__winid > 0 and self.__vim.call(
                'win_gotoid', self.__winid):
            # Move the window to bottom
            self.__vim.command('wincmd J')
        else:
            # Create new buffer
            self.__vim.command('botright new denite')
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
        self.__window_options['cursorline'] = True
        self.__window_options['colorcolumn'] = ''
        self.__window_options['number'] = False
        self.__window_options['relativenumber'] = False
        self.__window_options['foldenable'] = False
        self.__window_options['foldcolumn'] = 0

        self.__bufnr = self.__vim.current.buffer.number
        self.__winid = self.__vim.call('win_getid')

    def init_cursor(self):
        self.__cursor = 0
        self.__win_cursor = 1

    def update_buffer(self):
        prev_len = len(self.__candidates)
        self.__candidates = []
        statusline = '--' + self.__current_mode + '-- '
        for name, all, candidates in self.__denite.filter_candidates(
                self.__context):
            if len(all) == 0:
                continue
            self.__candidates += candidates
            statusline += '{}({}/{}) '.format(name, len(candidates), len(all))
        if self.__denite.is_async():
            statusline = '[async] ' + statusline
        self.__candidates_len = len(self.__candidates)
        statusline += '%=[{}] {:3}/{:4}'.format(
            self.__context['path'],
            self.__cursor + self.__win_cursor,
            self.__candidates_len)
        self.__window_options['statusline'] = statusline

        del self.__vim.current.buffer[:]
        self.__vim.current.buffer.append(
            [x.get('abbr', x['word']) for x in
             self.__candidates[self.__cursor:
                               self.__cursor + self.__winheight]])
        del self.__vim.current.buffer[0]

        self.__options['modified'] = False

        if prev_len > self.__candidates_len:
            self.init_cursor()

        self.move_cursor()

    def move_cursor(self):
        self.__vim.call('cursor', [self.__win_cursor, 1])
        if self.__context['auto_preview']:
            self.do_action(self.__context, 'preview')

    def change_mode(self, mode):
        custom = self.__context['custom']['map']

        self.__current_mode = mode
        self.__current_mappings = self.__default_mappings['_'].copy()
        if '_' in custom:
            self.__current_mappings.update(custom['_'])

        if mode in self.__default_mappings:
            self.__current_mappings.update(self.__default_mappings[mode])
        if mode in custom:
            self.__current_mappings.update(custom[mode])

        self.update_buffer()

    def quit_buffer(self):
        self.__vim.command('redraw | echo')
        self.__vim.command('pclose!')

        if not self.__vim.call('bufexists', self.__bufnr):
            return
        self.__vim.call('win_gotoid', self.__prev_winid)
        self.__vim.command('silent bdelete! ' + str(self.__bufnr))

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
        self.update_buffer()
        self.update_prompt()
        self.__win_cursor = 1

    def redraw(self):
        self.__context['is_redraw'] = True
        self.__denite.gather_candidates(self.__context)
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
            try:
                if is_async:
                    time.sleep(0.005)
                    nr = self.__vim.call('denite#util#getchar', 0)
                else:
                    nr = self.__vim.call('denite#util#getchar')
            except:
                self.quit()
                break

            char = nr if isinstance(nr, str) else chr(nr)

            mapping = self.__current_mappings.get(str(nr), None)
            if not mapping:
                mapping = self.__current_mappings.get(char, None)
            if mapping:
                map_args = re.split(':', mapping)
                arg = ':'.join(map_args[1:])
                if hasattr(self, map_args[0]):
                    func = getattr(self, map_args[0])
                    ret = func() if len(map_args) == 1 else func(arg)
                    if ret:
                        break
                    continue
            elif self.__current_mode == 'insert' and not isinstance(
                    nr, str) and nr >= 0x20:
                # Normal input string
                self.__input_before += char
                self.update_input()
                continue

            if is_async:
                self.update_buffer()

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
            kind = self.__denite.get_sources()[candidate['source']].kind

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
        self.update_buffer()
        self.move_cursor()

    def move_to_prev_line(self):
        if self.__win_cursor > 1:
            self.__win_cursor -= 1
        elif self.__cursor >= 1:
            self.__cursor -= 1
        self.update_buffer()
        self.move_cursor()

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
