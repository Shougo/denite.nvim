# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================
import re
import weakref
from itertools import filterfalse, groupby, takewhile

from denite.util import escape_syntax
from .action import DEFAULT_ACTION_KEYMAP
from .prompt import DenitePrompt
from .. import denite
from ..prompt.prompt import STATUS_ACCEPT, STATUS_INTERRUPT


class Default(object):
    @property
    def is_async(self):
        return self.__denite.is_async()

    @property
    def current_mode(self):
        return self.__current_mode

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
        self.__scroll = 0
        self.__is_multi = False
        self.__matched_pattern = ''
        self.__statusline_sources = ''
        self.__prompt = DenitePrompt(
            self.__vim,
            self.__context,
            weakref.proxy(self)
        )

    def start(self, sources, context):
        if self.__initialized and context['resume']:
            # Skip the initialization
            self.__current_mode = context['mode']
            self.__context['immediately'] = context['immediately']
            self.__context['cursor_wrap'] = context['cursor_wrap']

            self.init_buffer()
            self.change_mode(self.__current_mode)
            if context['select'] == '+1':
                self.move_to_next_line()
            elif context['select'] == '-1':
                self.move_to_prev_line()
            if self.check_empty():
                return self.__result
        else:
            self.__context.clear()
            self.__context.update(context)
            self.__context['sources'] = sources
            self.__context['is_redraw'] = False
            self.__current_mode = context['mode']
            self.__is_multi = len(sources) > 1

            self.__denite.start(self.__context)

            self.__denite.on_init(self.__context)

            self.__initialized = True

            self.__denite.gather_candidates(self.__context)
            self.update_candidates()
            if self.check_empty():
                return self.__result

            self.init_buffer()
            self.init_cursor()
            if self.__context['select'].isnumeric():
                self.__win_cursor = int(self.__context['select']) + 1
                self.move_cursor()

            self.change_mode(self.__current_mode)

        # Make sure that the caret position is ok
        self.__prompt.caret.locus = self.__prompt.caret.tail
        status = self.__prompt.start()
        if status == STATUS_INTERRUPT:
            # STATUS_INTERRUPT is returned when user hit <C-c> and the loop has
            # interrupted.
            # In this case, denite cancel any operation and close its window.
            self.quit()
        return self.__result

    def init_buffer(self):
        self.__winheight = int(self.__context['winheight'])
        self.__prev_winid = self.__vim.call('win_getid')
        self.__prev_bufnr = self.__vim.current.buffer.number
        self.__prev_tabpages = self.__vim.call('tabpagebuflist')
        self.__winrestcmd = self.__vim.call('winrestcmd')
        self.__winsaveview = self.__vim.call('winsaveview')
        self.__scroll = int(self.__context['scroll'])
        if self.__scroll == 0:
            self.__scroll = round(self.__winheight / 2)

        if self.__winid > 0 and self.__vim.call(
                'win_gotoid', self.__winid):
            # Move the window to bottom
            self.__vim.command('wincmd J')
        else:
            # Create new buffer
            self.__vim.command('silent ' +
                               self.__context['direction'] + ' new denite')
        self.resize_buffer()
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
        self.__vim.command('highlight default link deniteMatched Underlined')
        self.__vim.command('highlight default link deniteMatchedChar Search')
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
        self.__win_cursor = 1
        self.__cursor = 0
        if self.__context['reversed']:
            self.move_to_last_line()

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
        self.__vim.command('silent! syntax clear deniteMatchedChar')
        if self.__matched_pattern != '':
            self.__vim.command(
                'silent! syntax match deniteMatched /%s/ contained' % (
                    escape_syntax(self.__matched_pattern),
                )
            )
            self.__vim.command((
                'silent! syntax match deniteMatchedChar /[%s]/ '
                'containedin=deniteMatched'
            ) % re.sub(
                r'([[\]\\^-])',
                r'\\\1',
                self.__context['input'].replace(' ', '')
            ))

        del self.__vim.current.buffer[:]
        self.__vim.current.buffer.append(
            ['%s %s' % (
                x['source'] if self.__is_multi else '',
                x.get('abbr', x['word'])[:400])
             for x in self.__candidates[self.__cursor:
                                        self.__cursor + self.__winheight]])
        del self.__vim.current.buffer[0]
        self.resize_buffer()

        self.__options['modified'] = False

        self.move_cursor()

    def resize_buffer(self):
        winheight = self.__winheight
        if (self.__context['auto_resize'] and
                self.__candidates_len < self.__winheight):
            winheight = self.__candidates_len
        self.__vim.command('resize ' + str(winheight))

    def check_empty(self):
        if self.__candidates and self.__context['immediately']:
            self.do_action('default')
            return True
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

            if pattern == '':
                matchers = self.__denite.get_source(name).matchers
                pattern = next(filterfalse(
                    lambda x: x == '',
                    [self.__denite.get_filter(x).convert_pattern(
                        self.__context['input']) for x in matchers
                     if self.__denite.get_filter(x)]), '')
        self.__matched_pattern = pattern
        self.__candidates_len = len(self.__candidates)
        if self.__context['reversed']:
            self.__candidates.reverse()

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
            self.do_action('preview')
        if self.__context['auto_highlight']:
            self.do_action('highlight')

    def change_mode(self, mode):
        self.__current_mode = mode
        custom = self.__context['custom']['map']

        # Clear current keymap
        self.__prompt.keymap.registry.clear()

        # Apply mode independent mappings
        self.__prompt.keymap.register_from_rules(
            self.__vim,
            DEFAULT_ACTION_KEYMAP.get('_', [])
        )
        self.__prompt.keymap.register_from_rules(
            self.__vim,
            custom.get('_', [])
        )

        # Apply mode depend mappings
        mode = self.__current_mode
        self.__prompt.keymap.register_from_rules(
            self.__vim,
            DEFAULT_ACTION_KEYMAP.get(mode, [])
        )
        self.__prompt.keymap.register_from_rules(
            self.__vim,
            custom.get(mode, [])
        )

        # Update mode indicator
        self.update_buffer()

    def quit_buffer(self):
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

    def get_current_candidates(self):
        if self.__cursor >= self.__candidates_len:
            return []
        return [self.__candidates[self.__cursor + self.__win_cursor - 1]]

    def redraw(self):
        self.__context['is_redraw'] = True
        self.__denite.gather_candidates(self.__context)
        self.update_candidates()
        self.update_buffer()
        self.__context['is_redraw'] = False

    def quit(self):
        self.__denite.on_close(self.__context)
        self.quit_buffer()
        self.__result = []
        return STATUS_ACCEPT

    def do_action(self, action):
        candidates = self.get_current_candidates()
        if not candidates:
            return

        prev_id = self.__vim.call('win_getid')
        is_denite = self.__vim.eval('&filetype') == 'denite'
        self.__context['__prev_winid'] = prev_id
        if is_denite:
            self.__vim.call('win_gotoid', self.__prev_winid)
            now_id = self.__vim.call('win_getid')
            if prev_id == now_id:
                # The previous window search is failed.
                # Jump to the other window.
                if len(self.__vim.windows) == 1:
                    self.__vim.command('topleft new')
                else:
                    self.__vim.command('wincmd w')

        is_quit = not self.__denite.do_action(
            self.__context, action, candidates)

        if is_denite:
            now_id = self.__vim.call('win_getid')
            if now_id != self.__prev_winid:
                self.__prev_winid = now_id
                self.__prev_bufnr = self.__vim.current.buffer.number
            self.__vim.call('win_gotoid', prev_id)

        if is_quit:
            self.__denite.on_close(self.__context)
            if self.__context['quit']:
                self.quit_buffer()
            else:
                # Disable quit flag
                is_quit = False
        self.__result = candidates
        return STATUS_ACCEPT if is_quit else None

    def choose_action(self):
        candidates = self.get_current_candidates()
        if not candidates:
            return

        self.__vim.vars['denite#_actions'] = self.__denite.get_actions(
            self.__context, candidates)
        action = self.__vim.call('input', 'Action: ', '',
                                 'customlist,denite#helper#complete_actions')
        if action == '':
            return
        return self.do_action(action)

    def move_to_next_line(self):
        if (self.__win_cursor < self.__candidates_len and
                self.__win_cursor < self.__winheight):
            self.__win_cursor += 1
        elif self.__win_cursor + self.__cursor < self.__candidates_len:
            self.__cursor += 1
        elif self.__context['cursor_wrap']:
            self.move_to_first_line()
        else:
            return
        self.update_buffer()

    def move_to_prev_line(self):
        if self.__win_cursor > 1:
            self.__win_cursor -= 1
        elif self.__cursor >= 1:
            self.__cursor -= 1
        elif self.__context['cursor_wrap']:
            self.move_to_last_line()
        else:
            return
        self.update_buffer()

    def move_to_first_line(self):
        if self.__win_cursor > 1 or self.__cursor > 0:
            self.__win_cursor = 1
            self.__cursor = 0
            self.update_buffer()

    def move_to_last_line(self):
        win_max = min(self.__candidates_len, self.__winheight)
        cur_max = self.__candidates_len - win_max
        if self.__win_cursor < win_max or self.__cursor < cur_max:
            self.__win_cursor = win_max
            self.__cursor = cur_max
            self.update_buffer()

    def scroll_window_upwards(self):
        self.scroll_up(self.__scroll)

    def scroll_window_downwards(self):
        self.scroll_down(self.__scroll)

    def scroll_page_backwards(self):
        self.scroll_up(self.__winheight - 1)

    def scroll_page_forwards(self):
        self.scroll_down(self.__winheight - 1)

    def scroll_down(self, scroll):
        if (self.__win_cursor < self.__candidates_len and
                self.__win_cursor < self.__winheight):
            self.__win_cursor = min(self.__win_cursor + scroll,
                                    self.__candidates_len, self.__winheight)
        elif self.__win_cursor + self.__cursor < self.__candidates_len:
            self.__cursor = min(self.__cursor + scroll,
                                self.__candidates_len - self.__win_cursor)
        else:
            return
        self.update_buffer()

    def scroll_up(self, scroll):
        if self.__win_cursor > 1:
            self.__win_cursor = max(self.__win_cursor - scroll, 1)
        elif self.__cursor > 0:
            self.__cursor = max(self.__cursor - scroll, 0)
        else:
            return
        self.update_buffer()

    def jump_to_next_source(self):
        if len(self.__context['sources']) == 1:
            return

        current_index = self.__cursor + self.__win_cursor - 1
        forward_candidates = self.__candidates[current_index:]
        forward_sources = groupby(
            forward_candidates,
            lambda candidate: candidate['source']
        )
        forward_times = len(list(next(forward_sources)[1]))
        remaining_candidates = self.__candidates_len - current_index \
            - forward_times
        if next(forward_sources, None) is None:
            # If the cursor is on the last source
            self.__cursor = 0
            self.__win_cursor = 1
        elif self.__candidates_len < self.__winheight:
            # If there is a space under the candidates
            self.__cursor = 0
            self.__win_cursor += forward_times
        elif remaining_candidates < self.__winheight:
            self.__cursor = self.__candidates_len - self.__winheight + 1
            self.__win_cursor = self.__winheight - remaining_candidates
        else:
            self.__cursor += forward_times + self.__win_cursor - 1
            self.__win_cursor = 1

        self.update_buffer()

    def jump_to_prev_source(self):
        if len(self.__context['sources']) == 1:
            return

        current_index = self.__cursor + self.__win_cursor - 1
        backward_candidates = reversed(self.__candidates[:current_index + 1])
        backward_sources = groupby(
            backward_candidates,
            lambda candidate: candidate['source']
        )
        current_source = list(next(backward_sources)[1])
        try:
            prev_source = list(next(backward_sources)[1])
        except StopIteration:  # If the cursor is on the first source
            last_source = takewhile(
                lambda candidate:
                    candidate['source'] == self.__candidates[-1]['source'],
                reversed(self.__candidates)
            )
            len_last_source = len(list(last_source))
            if self.__candidates_len < self.__winheight:
                self.__cursor = 0
                self.__win_cursor = self.__candidates_len - len_last_source + 1
            elif len_last_source < self.__winheight:
                self.__cursor = self.__candidates_len - self.__winheight + 1
                self.__win_cursor = self.__winheight - len_last_source
            else:
                self.__cursor = self.__candidates_len - len_last_source
                self.__win_cursor = 1
        else:
            back_times = len(current_source) - 1 + len(prev_source)
            remaining_candidates = self.__candidates_len - current_index \
                + back_times
            if self.__candidates_len < self.__winheight:
                self.__cursor = 0
                self.__win_cursor -= back_times
            elif remaining_candidates < self.__winheight:
                self.__cursor = self.__candidates_len - self.__winheight + 1
                self.__win_cursor = self.__winheight - remaining_candidates
            else:
                self.__cursor -= back_times - self.__win_cursor + 1
                self.__win_cursor = 1

        self.update_buffer()

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
        return STATUS_ACCEPT
