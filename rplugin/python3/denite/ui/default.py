# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import copy
import re
import weakref
from itertools import groupby, takewhile

from denite.util import (
    clear_cmdline, echo, error, regex_convert_py_vim, clearmatch)
from .action import DEFAULT_ACTION_KEYMAP
from .prompt import DenitePrompt
from denite.parent import SyncParent
from ..prompt.prompt import STATUS_ACCEPT, STATUS_INTERRUPT


class Default(object):
    @property
    def is_async(self):
        return self._denite.is_async()

    @property
    def current_mode(self):
        return self._current_mode

    def __init__(self, vim):
        self._vim = vim
        self._denite = None
        self._cursor = 0
        self._win_cursor = 1
        self._selected_candidates = []
        self._candidates = []
        self._candidates_len = 0
        self._result = []
        self._context = {}
        self._current_mode = ''
        self._mode_stack = []
        self._current_mappings = {}
        self._bufnr = -1
        self._winid = -1
        self._winrestcmd = ''
        self._initialized = False
        self._winheight = 0
        self._winwidth = 0
        self._winminheight = -1
        self._scroll = 0
        self._is_multi = False
        self._matched_pattern = ''
        self._displayed_texts = []
        self._statusline_sources = ''
        self._prompt = DenitePrompt(
            self._vim,
            self._context,
            weakref.proxy(self)
        )
        self._guicursor = ''
        self._titlestring = ''
        self._ruler = False
        self._prev_action = ''
        self._prev_status = {}
        self._prev_curpos = []
        self._is_suspend = False
        self._save_window_options = {}
        self._sources_history = []

    def start(self, sources, context):
        if not self._denite:
            self._denite = SyncParent(self._vim)

        self._result = []
        context['sources_queue'] = [sources]
        self._sources_history = []
        try:
            while context['sources_queue']:
                prev_history = copy.copy(self._sources_history)
                prev_path = context['path']

                self._start(context['sources_queue'][0], context)

                if prev_history == self._sources_history:
                    self._sources_history.append({
                        'sources': context['sources_queue'][0],
                        'path': prev_path,
                    })

                context['sources_queue'].pop(0)
                context['path'] = self._context['path']
        finally:
            self.cleanup()

        return self._result

    def _start(self, sources, context):
        self._vim.command('silent! autocmd! denite')

        if re.search(r'\[Command Line\]$', self._vim.current.buffer.name):
            # Ignore command line window.
            return

        if self._initialized and context['resume']:
            # Skip the initialization

            if not self._is_suspend:
                if context['mode']:
                    self._current_mode = context['mode']

                update = ('immediately', 'immediately_1',
                          'cursor_wrap', 'cursor_pos', 'prev_winid',
                          'quick_move')
                for key in update:
                    self._context[key] = context[key]

            if self.check_option():
                return

            self.init_buffer()
            if context['refresh']:
                self.redraw()
        else:
            if not context['mode']:
                # Default mode
                context['mode'] = 'insert'

            self._context.clear()
            self._context.update(context)
            self._context['sources'] = sources
            self._context['is_redraw'] = False
            self._current_mode = context['mode']
            self._is_multi = len(sources) > 1

            if not sources:
                # Ignore empty sources.
                error(self._vim, 'Empty sources')
                return

            self.init_denite()
            self.gather_candidates()
            self.update_candidates()
            self.init_cursor()

            if self.check_option():
                return

            self.init_buffer()

        self._is_suspend = False
        self.update_displayed_texts()
        self.change_mode(self._current_mode)
        self.update_buffer()

        if self._context['quick_move'] and self.quick_move():
            return

        # Make sure that the caret position is ok
        self._prompt.caret.locus = self._prompt.caret.tail
        status = self._prompt.start()
        if status == STATUS_INTERRUPT:
            # STATUS_INTERRUPT is returned when user hit <C-c> and the loop has
            # interrupted.
            # In this case, denite cancel any operation and close its window.
            self.quit()
        return

    def init_buffer(self):
        self._prev_status = dict()
        self._displayed_texts = []

        if not self._is_suspend:
            self._prev_bufnr = self._vim.current.buffer.number
            self._prev_curpos = self._vim.call('getcurpos')
            self._prev_wininfo = self._get_wininfo()
            self._prev_winid = int(self._context['prev_winid'])
            self._winrestcmd = self._vim.call('winrestcmd')

        self._scroll = int(self._context['scroll'])
        if self._scroll == 0:
            self._scroll = round(self._winheight / 2)
        if self._context['cursor_shape']:
            self._guicursor = self._vim.options['guicursor']
            self._vim.options['guicursor'] = 'a:None'
        self._titlestring = self._vim.options['titlestring']
        self._ruler = self._vim.options['ruler']

        self._switch_buffer()
        self.resize_buffer()

        self._winheight = self._vim.current.window.height
        self._winwidth = self._vim.current.window.width

        self._options = self._vim.current.buffer.options
        self._options['buftype'] = 'nofile'
        self._options['bufhidden'] = 'delete'
        self._options['swapfile'] = False
        self._options['buflisted'] = False
        self._options['modeline'] = False
        self._options['filetype'] = 'denite'
        self._options['modifiable'] = True

        if self._context['split'] == 'floating':
            # Disable ruler
            self._vim.options['ruler'] = False

        self._window_options = self._vim.current.window.options
        window_options = {
            'colorcolumn': '',
            'conceallevel': 3,
            'concealcursor': 'n',
            'cursorcolumn': False,
            'foldenable': False,
            'foldcolumn': 0,
            'list': False,
            'number': False,
            'relativenumber': False,
            'spell': False,
            'winfixheight': True,
            'wrap': False,
        }
        if self._context['cursorline']:
            window_options['cursorline'] = True
        self._save_window_options = {}
        for k, v in window_options.items():
            self._save_window_options[k] = self._window_options[k]
            self._window_options[k] = v

        self._bufvars = self._vim.current.buffer.vars
        self._bufnr = self._vim.current.buffer.number
        self._winid = self._vim.call('win_getid')

        self._bufvars['denite_statusline'] = {}

        self._vim.vars['denite#_previewed_buffers'] = {}

        self._vim.command('silent doautocmd WinEnter')
        self._vim.command('silent doautocmd BufWinEnter')
        self._vim.command('doautocmd FileType denite')

        self.init_syntax()

    def _switch_buffer(self):
        split = self._context['split']
        if (split != 'no' and self._winid > 0 and
                self._vim.call('win_gotoid', self._winid)):
            if (not self._is_suspend and
                    split != 'vertical' and split != 'floating'):
                # Move the window to bottom
                self._vim.command('wincmd J')
            self._winrestcmd = ''
        else:
            command = 'edit'
            if split == 'tab':
                self._vim.command('tabnew')
            elif (split == 'floating' and
                  self._vim.call('exists', '*nvim_open_win')):
                # Use floating window
                self._vim.call(
                    'nvim_open_win',
                    self._vim.call('bufnr', '%'), True, {
                        'relative': 'editor',
                        'row': int(self._context['winrow']),
                        'col': int(self._context['wincol']),
                        'width': int(self._context['winwidth']),
                        'height': int(self._context['winheight']),
                    })
            elif split != 'no':
                command = self._get_direction()
                command += ' vsplit' if split == 'vertical' else ' split'
            self._vim.call(
                'denite#util#execute_path',
                f'silent keepalt {command}', '[denite]')

    def _get_direction(self):
        direction = self._context['direction']
        if direction == 'dynamictop' or direction == 'dynamicbottom':
            self.update_displayed_texts()
            winwidth = self._vim.call('winwidth', 0)
            is_fit = not [x for x in self._displayed_texts
                          if self._vim.call('strwidth', x) > winwidth]
            if direction == 'dynamictop':
                direction = 'aboveleft' if is_fit else 'topleft'
            else:
                direction = 'belowright' if is_fit else 'botright'
        return direction

    def _get_wininfo(self):
        return [
            self._vim.options['columns'], self._vim.options['lines'],
            self._vim.call('win_getid'),
        ]

    def _switch_prev_buffer(self):
        if (self._prev_bufnr == self._bufnr or
                self._vim.buffers[self._prev_bufnr].name == ''):
            self._vim.command('enew')
        else:
            self._vim.command('buffer ' + str(self._prev_bufnr))

    def init_syntax(self):
        self._vim.command('syntax case ignore')
        self._vim.command('highlight default link deniteMode ModeMsg')
        self._vim.command('highlight link deniteMatchedRange ' +
                          self._context['highlight_matched_range'])
        self._vim.command('highlight link deniteMatchedChar ' +
                          self._context['highlight_matched_char'])
        self._vim.command('highlight default link ' +
                          'deniteStatusLinePath Comment')
        self._vim.command('highlight default link ' +
                          'deniteStatusLineNumber LineNR')
        self._vim.command('highlight default link ' +
                          'deniteSelectedLine Statement')

        self._vim.command(('syntax match deniteSelectedLine /^[%s].*/' +
                           ' contains=deniteConcealedMark') % (
                               self._context['selected_icon']))
        self._vim.command(('syntax match deniteConcealedMark /^[ %s]/' +
                           ' conceal contained') % (
                               self._context['selected_icon']))

        self._denite.init_syntax(self._context, self._is_multi)

    def init_cursor(self):
        self._win_cursor = 1
        self._cursor = 0
        if self._context['reversed']:
            self.move_to_last_line()

    def update_candidates(self):
        (pattern, statuses,
         self._candidates) = self._denite.filter_candidates(self._context)

        prev_matched_pattern = self._matched_pattern
        self._matched_pattern = pattern
        self._candidates_len = len(self._candidates)

        self._statusline_sources = ' '.join(statuses)

        prev_displayed_texts = self._displayed_texts
        self.update_displayed_texts()

        updated = (self._displayed_texts != prev_displayed_texts or
                   self._matched_pattern != prev_matched_pattern)
        if updated and self._denite.is_async() and self._context['reversed']:
            self.init_cursor()

        return updated

    def update_displayed_texts(self):
        if self._context['auto_resize']:
            winminheight = int(self._context['winminheight'])
            if (winminheight is not -1 and
                    self._candidates_len < winminheight):
                self._winheight = winminheight
            elif self._candidates_len > int(self._context['winheight']):
                self._winheight = int(self._context['winheight'])
            elif self._candidates_len != self._winheight:
                self._winheight = self._candidates_len

        self._displayed_texts = [
            self.get_candidate_display_text(i)
            for i in range(self._cursor,
                           min(self._candidates_len,
                               self._cursor + self._winheight))
        ]

    def update_buffer(self):
        if self._bufnr != self._vim.current.buffer.number:
            return

        self.update_status()

        if self._vim.call('hlexists', 'deniteMatchedRange'):
            self._vim.command('silent! syntax clear deniteMatchedRange')
        if self._vim.call('hlexists', 'deniteMatchedChar'):
            self._vim.command('silent! syntax clear deniteMatchedChar')
        if self._matched_pattern != '':
            self._vim.command(
                r'silent! syntax match deniteMatchedRange /\c%s/ contained' %
                (regex_convert_py_vim(self._matched_pattern))
            )
            self._vim.command((
                'silent! syntax match deniteMatchedChar /[%s]/ '
                'containedin=deniteMatchedRange contained'
            ) % re.sub(
                r'([\[\]\\^-])',
                r'\\\1',
                self._context['input'].replace(' ', '')
            ))

        self._vim.current.buffer[:] = self._displayed_texts
        self.resize_buffer()

        self.move_cursor()

    def update_status(self):
        raw_mode = self._current_mode.upper()
        cursor_location = self._cursor + self._win_cursor
        max_len = len(str(self._candidates_len))
        linenr = ('{:'+str(max_len)+'}/{:'+str(max_len)+'}').format(
            cursor_location,
            self._candidates_len)
        mode = '-- ' + raw_mode + ' -- '
        if self._context['error_messages']:
            mode = '[ERROR] ' + mode
        path = '[' + self._context['path'] + ']'

        status = {
            'mode': mode,
            'sources': self._statusline_sources,
            'path': path,
            'linenr': linenr,
            # Extra
            'raw_mode': raw_mode,
            'buffer_name': self._context['buffer_name'],
            'line_cursor': cursor_location,
            'line_total': self._candidates_len,
        }
        if status != self._prev_status:
            self._bufvars['denite_statusline'] = status
            self._vim.command('redrawstatus')
            self._prev_status = status

        if self._context['statusline']:
            status = (
                "%#deniteMode#%{denite#get_status('mode')}%* " +
                "%{denite#get_status('sources')} %=" +
                "%#deniteStatusLinePath# %{denite#get_status('path')} %*" +
                "%#deniteStatusLineNumber#%{denite#get_status('linenr')}%*")
            if self._context['split'] == 'floating':
                self._vim.options['titlestring'] = status
            else:
                self._window_options['statusline'] = status

    def update_cursor(self):
        self.update_displayed_texts()
        self.update_buffer()

    def get_display_source_name(self, name):
        source_names = self._context['source_names']
        if not self._is_multi or source_names == 'hide':
            source_name = ''
        else:
            short_name = (re.sub(r'([a-zA-Z])[a-zA-Z]+', r'\1', name)
                          if re.search(r'[^a-zA-Z]', name) else name[:2])
            source_name = short_name if source_names == 'short' else name
        return source_name

    def get_candidate_display_text(self, index):
        source_names = self._context['source_names']
        candidate = self._candidates[index]
        terms = []
        if self._is_multi and source_names != 'hide':
            terms.append(self.get_display_source_name(
                candidate['source_name']))
        encoding = self._context['encoding']
        abbr = candidate.get('abbr', candidate['word']).encode(
            encoding, errors='replace').decode(encoding, errors='replace')
        terms.append(abbr[:int(self._context['max_candidate_width'])])
        return (self._context['selected_icon']
                if index in self._selected_candidates
                else ' ') + ' '.join(terms).replace('\n', '')

    def resize_buffer(self):
        split = self._context['split']
        if split == 'no' or split == 'tab':
            return

        winheight = self._winheight
        winwidth = self._winwidth
        is_vertical = split == 'vertical'

        if not is_vertical and self._vim.current.window.height != winheight:
            self._vim.command('resize ' + str(winheight))
            if self._context['reversed']:
                self._vim.command('normal! zb')
        elif is_vertical and self._vim.current.window.width != winwidth:
            self._vim.command('vertical resize ' + str(winwidth))

    def check_option(self):
        if self._context['cursor_pos'].isnumeric():
            self.init_cursor()
            self.move_to_pos(int(self._context['cursor_pos']))
        elif re.match(r'\+\d+', self._context['cursor_pos']):
            for _ in range(int(self._context['cursor_pos'][1:])):
                self.move_to_next_line()
        elif re.match(r'-\d+', self._context['cursor_pos']):
            for _ in range(int(self._context['cursor_pos'][1:])):
                self.move_to_prev_line()
        elif self._context['cursor_pos'] == '$':
            self.move_to_last_line()
        elif self._context['do'] != '':
            self.do_command(self._context['do'])
            return True

        if (self._candidates and self._context['immediately'] or
                len(self._candidates) == 1 and self._context['immediately_1']):
            self.do_immediately()
            return True
        return not (self._context['empty'] or
                    self._denite.is_async() or self._candidates)

    def do_immediately(self):
        goto = self._winid > 0 and self._vim.call(
            'win_gotoid', self._winid)
        if goto:
            # Jump to denite window
            self.init_buffer()
            self.update_cursor()
        self.do_action('default')
        candidate = self.get_cursor_candidate()
        echo(self._vim, 'Normal', '[{}/{}] {}'.format(
            self._cursor + self._win_cursor, self._candidates_len,
            candidate.get('abbr', candidate['word'])))
        if goto:
            # Move to the previous window
            self.suspend()
            self._vim.command('wincmd p')

    def do_command(self, command):
        self.init_cursor()
        self._context['post_action'] = 'suspend'
        while self._cursor + self._win_cursor < self._candidates_len:
            self.do_action('default', command)
            self.move_to_next_line()
        self.quit_buffer()

    def move_cursor(self):
        if self._win_cursor > self._vim.call('line', '$'):
            self._win_cursor = self._vim.call('line', '$')
        if self._win_cursor != self._vim.call('line', '.'):
            self._vim.call('cursor', [self._win_cursor, 1])

        if self._context['auto_action']:
            self.do_action(self._context['auto_action'])

    def change_mode(self, mode):
        self._current_mode = mode
        custom = self._context['custom']['map']
        use_default_mappings = self._context['use_default_mappings']

        highlight = 'highlight_mode_' + mode
        if highlight in self._context:
            self._vim.command('highlight! link CursorLine ' +
                              self._context[highlight])

        # Clear current keymap
        self._prompt.keymap.registry.clear()

        # Apply mode independent mappings
        if use_default_mappings:
            self._prompt.keymap.register_from_rules(
                self._vim,
                DEFAULT_ACTION_KEYMAP.get('_', [])
            )
        self._prompt.keymap.register_from_rules(
            self._vim,
            custom.get('_', [])
        )

        # Apply mode depend mappings
        mode = self._current_mode
        if use_default_mappings:
            self._prompt.keymap.register_from_rules(
                self._vim,
                DEFAULT_ACTION_KEYMAP.get(mode, [])
            )
        self._prompt.keymap.register_from_rules(
            self._vim,
            custom.get(mode, [])
        )

        # Update mode context
        self._context['mode'] = mode

        # Update mode indicator
        self.update_status()

    def cleanup(self):
        # Clear previewed buffers
        if not self._is_suspend and not self._context['has_preview_window']:
            self._vim.command('pclose!')
        for bufnr in self._vim.vars['denite#_previewed_buffers'].keys():
            if not self._vim.call('win_findbuf', bufnr):
                self._vim.command('silent bdelete ' + str(bufnr))
        self._vim.vars['denite#_previewed_buffers'] = {}

        clearmatch(self._vim)

        if not self._context['immediately']:
            # Redraw to clear prompt
            self._vim.command('redraw | echo ""')
        self._vim.command('highlight! link CursorLine CursorLine')
        if self._context['cursor_shape']:
            self._vim.command('set guicursor&')
            self._vim.options['guicursor'] = self._guicursor
        if self._context['split'] == 'floating':
            self._vim.options['titlestring'] = self._titlestring
            self._vim.options['ruler'] = self._ruler

    def quit_buffer(self):
        self.cleanup()
        if self._vim.call('bufwinnr', self._bufnr) < 0:
            # Denite buffer is already closed
            return

        # Restore the window
        if self._context['split'] == 'no':
            self._window_options['cursorline'] = False
            self._switch_prev_buffer()
            for k, v in self._save_window_options.items():
                self._vim.current.window.options[k] = v
        else:
            if self._context['split'] == 'tab':
                self._vim.command('tabclose!')

            if self._context['split'] != 'tab':
                self._vim.command('close!')

            self._vim.call('win_gotoid', self._prev_winid)

        # Restore the position
        self._vim.call('setpos', '.', self._prev_curpos)

        if self._get_wininfo() and self._get_wininfo() == self._prev_wininfo:
            self._vim.command(self._winrestcmd)

    def get_cursor_candidate(self):
        if self._cursor + self._win_cursor > self._candidates_len:
            return {}
        return self._candidates[self._cursor + self._win_cursor - 1]

    def get_selected_candidates(self):
        if not self._selected_candidates:
            return [self.get_cursor_candidate()
                    ] if self.get_cursor_candidate() else []
        return [self._candidates[x] for x in self._selected_candidates]

    def redraw(self, is_force=True):
        self._context['is_redraw'] = is_force
        if is_force:
            self.gather_candidates()
        if self.update_candidates():
            self.update_buffer()
        else:
            self.update_status()
        self._context['is_redraw'] = False

    def quit(self):
        self._denite.on_close(self._context)
        self.quit_buffer()
        self._result = []
        return STATUS_ACCEPT

    def restart(self):
        self.quit_buffer()
        self.init_denite()
        self.gather_candidates()
        self.init_buffer()
        self.update_candidates()
        self.change_mode(self._current_mode)
        self.update_buffer()

    def restore_sources(self, context):
        if not self._sources_history:
            return

        history = self._sources_history[-1]
        context['sources_queue'].append(history['sources'])
        context['path'] = history['path']
        self._sources_history.pop()
        return STATUS_ACCEPT

    def init_denite(self):
        self._mode_stack = []
        self._prompt.history.reset()
        self._denite.start(self._context)
        self._denite.on_init(self._context)
        self._initialized = True
        self._winheight = int(self._context['winheight'])
        self._winwidth = int(self._context['winwidth'])

    def gather_candidates(self):
        self._selected_candidates = []
        self._denite.gather_candidates(self._context)

    def do_action(self, action_name, command=''):
        candidates = self.get_selected_candidates()
        if not candidates or not action_name:
            return

        self._prev_action = action_name
        action = self._denite.get_action(
            self._context, action_name, candidates)
        if not action:
            # Search the prefix.
            prefix_actions = [x for x in
                              self._denite.get_action_names(
                                  self._context, candidates)
                              if x.startswith(action_name)]
            if not prefix_actions:
                return
            action_name = prefix_actions[0]
            action = self._denite.get_action(
                self._context, action_name, candidates)

        post_action = self._context['post_action']

        is_quit = action['is_quit'] or post_action == 'quit'
        if is_quit:
            self.quit()

        self._denite.do_action(self._context, action_name, candidates)
        self._result = candidates
        if command != '':
            self._vim.command(command)

        if is_quit and (post_action == 'open' or post_action == 'suspend'):
            # Re-open denite buffer

            self.init_buffer()
            self.change_mode(self._current_mode)

            self.redraw(False)
            # Disable quit flag
            is_quit = False

        if not is_quit:
            self._selected_candidates = []
            self.redraw(action['is_redraw'])

        if post_action == 'suspend':
            self.suspend()
            self._vim.command('wincmd p')
            return STATUS_ACCEPT

        return STATUS_ACCEPT if is_quit else None

    def choose_action(self):
        candidates = self.get_selected_candidates()
        if not candidates:
            return

        self._vim.vars['denite#_actions'] = self._denite.get_action_names(
            self._context, candidates)
        clear_cmdline(self._vim)
        action = self._vim.call('input', 'Action: ', '',
                                'customlist,denite#helper#complete_actions')
        if action == '':
            return
        return self.do_action(action)

    def move_to_pos(self, pos):
        self._cursor = int(pos / self._winheight) * self._winheight
        self._win_cursor = (pos % self._winheight) + 1
        self.update_cursor()

    def move_to_next_line(self):
        if self._win_cursor + self._cursor < self._candidates_len:
            if self._win_cursor < self._winheight:
                self._win_cursor += 1
            else:
                self._cursor += 1
        elif self._context['cursor_wrap']:
            self.move_to_first_line()
        else:
            return
        self.update_cursor()

    def move_to_prev_line(self):
        if self._win_cursor > 1:
            self._win_cursor -= 1
        elif self._cursor >= 1:
            self._cursor -= 1
        elif self._context['cursor_wrap']:
            self.move_to_last_line()
        else:
            return
        self.update_cursor()

    def move_to_first_line(self):
        if self._win_cursor > 1 or self._cursor > 0:
            self._win_cursor = 1
            self._cursor = 0
            self.update_cursor()

    def move_to_last_line(self):
        win_max = min(self._candidates_len, self._winheight)
        cur_max = self._candidates_len - win_max
        if self._win_cursor < win_max or self._cursor < cur_max:
            self._win_cursor = win_max
            self._cursor = cur_max
            self.update_cursor()

    def move_to_top(self):
        self._win_cursor = 1
        self.update_cursor()

    def move_to_middle(self):
        self._win_cursor = self._winheight // 2
        self.update_cursor()

    def move_to_bottom(self):
        self._win_cursor = self._winheight
        self.update_cursor()

    def scroll_window_upwards(self):
        self.scroll_up(self._scroll)

    def scroll_window_downwards(self):
        self.scroll_down(self._scroll)

    def scroll_page_backwards(self):
        self.scroll_up(self._winheight - 1)

    def scroll_page_forwards(self):
        self.scroll_down(self._winheight - 1)

    def scroll_down(self, scroll):
        if self._win_cursor + self._cursor < self._candidates_len:
            if self._win_cursor <= 1:
                self._win_cursor = 1
                self._cursor = min(self._cursor + scroll,
                                   self._candidates_len)
            elif self._win_cursor < self._winheight:
                self._win_cursor = min(
                    self._win_cursor + scroll,
                    self._candidates_len,
                    self._winheight)
            else:
                self._cursor = min(
                    self._cursor + scroll,
                    self._candidates_len - self._win_cursor)
        else:
            return
        self.update_cursor()

    def scroll_up(self, scroll):
        if self._win_cursor > 1:
            self._win_cursor = max(self._win_cursor - scroll, 1)
        elif self._cursor > 0:
            self._cursor = max(self._cursor - scroll, 0)
        else:
            return
        self.update_cursor()

    def scroll_window_up_one_line(self):
        if self._cursor < 1:
            return self.scroll_up(1)
        self._cursor -= 1
        self._win_cursor += 1
        self.update_cursor()

    def scroll_window_down_one_line(self):
        if self._win_cursor <= 1 and self._cursor > 0:
            return self.scroll_down(1)
        self._cursor += 1
        self._win_cursor -= 1
        self.update_cursor()

    def scroll_cursor_to_top(self):
        self._cursor += self._win_cursor - 1
        self._win_cursor = 1
        self.update_cursor()

    def scroll_cursor_to_middle(self):
        self.scroll_cursor_to_top()
        while self._cursor >= 1 and self._win_cursor < self._winheight // 2:
            self.scroll_window_up_one_line()

    def scroll_cursor_to_bottom(self):
        self.scroll_cursor_to_top()
        while self._cursor >= 1 and self._win_cursor < self._winheight:
            self.scroll_window_up_one_line()

    def jump_to_next_by(self, key):
        keyfunc = self._keyfunc(key)
        keys = [keyfunc(candidate) for candidate in self._candidates]
        if not keys or len(set(keys)) == 1:
            return

        current_index = self._cursor + self._win_cursor - 1
        forward_candidates = self._candidates[current_index:]
        forward_sources = groupby(forward_candidates, keyfunc)
        forward_times = len(list(next(forward_sources)[1]))
        if not forward_times:
            return
        remaining_candidates = (self._candidates_len - current_index
                                - forward_times)
        if next(forward_sources, None) is None:
            # If the cursor is on the last source
            self._cursor = 0
            self._win_cursor = 1
        elif self._candidates_len < self._winheight:
            # If there is a space under the candidates
            self._cursor = 0
            self._win_cursor += forward_times
        elif remaining_candidates < self._winheight:
            self._cursor = self._candidates_len - self._winheight + 1
            self._win_cursor = self._winheight - remaining_candidates
        else:
            self._cursor += forward_times + self._win_cursor - 1
            self._win_cursor = 1

        self.update_cursor()

    def jump_to_prev_by(self, key):
        keyfunc = self._keyfunc(key)
        keys = [keyfunc(candidate) for candidate in self._candidates]
        if not keys or len(set(keys)) == 1:
            return

        current_index = self._cursor + self._win_cursor - 1
        backward_candidates = reversed(self._candidates[:current_index + 1])
        backward_sources = groupby(backward_candidates, keyfunc)
        current_source = list(next(backward_sources)[1])
        try:
            prev_source = list(next(backward_sources)[1])
        except StopIteration:  # If the cursor is on the first source
            last_source = takewhile(
                lambda candidate:
                    keyfunc(candidate) == keyfunc(self._candidates[-1]),
                reversed(self._candidates)
            )
            len_last_source = len(list(last_source))
            if self._candidates_len < self._winheight:
                self._cursor = 0
                self._win_cursor = self._candidates_len - len_last_source + 1
            elif len_last_source < self._winheight:
                self._cursor = self._candidates_len - self._winheight + 1
                self._win_cursor = self._winheight - len_last_source
            else:
                self._cursor = self._candidates_len - len_last_source
                self._win_cursor = 1
        else:
            back_times = len(current_source) - 1 + len(prev_source)
            remaining_candidates = (self._candidates_len - current_index
                                    + back_times)
            if self._candidates_len < self._winheight:
                self._cursor = 0
                self._win_cursor -= back_times
            elif remaining_candidates < self._winheight:
                self._cursor = self._candidates_len - self._winheight + 1
                self._win_cursor = self._winheight - remaining_candidates
            else:
                self._cursor -= back_times - self._win_cursor + 1
                self._win_cursor = 1

        self.update_cursor()

    def quick_move(self):
        def get_quick_move_table():
            table = {}
            context = self._context
            base = self._win_cursor
            for [key, number] in context['quick_move_table'].items():
                number = int(number)
                pos = ((base - number) if context['reversed']
                       else (number + base))
                if pos > 0:
                    table[key] = pos
            return table

        def quick_move_redraw(table, is_define):
            bufnr = self._vim.current.buffer.number
            for [key, number] in table.items():
                signid = 2000 + number
                name = 'denite_quick_move_' + str(number)
                if is_define:
                    self._vim.command(
                        f'sign define {name} text={key} texthl=Special')
                    self._vim.command(
                        f'sign place {signid} name={name} '
                        f'line={number} buffer={bufnr}')
                else:
                    self._vim.command(
                        f'silent! sign unplace {signid} buffer={bufnr}')
                    self._vim.command('silent! sign undefine ' + name)

        quick_move_table = get_quick_move_table()
        self._vim.command('echo "Input quick match key: "')
        quick_move_redraw(quick_move_table, True)
        self._vim.command('redraw')

        char = ''
        while char == '':
            char = self._vim.call('nr2char',
                                  self._vim.call('denite#util#getchar'))

        quick_move_redraw(quick_move_table, False)

        if (char not in quick_move_table or
                quick_move_table[char] > self._winheight):
            return

        self._win_cursor = quick_move_table[char]
        self.update_cursor()

        if self._context['quick_move'] == 'immediately':
            self.do_action('default')
            return True

    def _keyfunc(self, key):
        def wrapped(candidate):
            for k in key, 'action__' + key:
                try:
                    return str(candidate[k])
                except Exception:
                    pass
            return ''
        return wrapped

    def enter_mode(self, mode):
        if mode == self._current_mode:
            return

        self._mode_stack.append(self._current_mode)
        self.change_mode(mode)

    def leave_mode(self):
        if not self._mode_stack:
            return self.quit()

        self._current_mode = self._mode_stack[-1]
        self._mode_stack = self._mode_stack[:-1]
        self.change_mode(self._current_mode)

    def suspend(self):
        if self._bufnr == self._vim.current.buffer.number:
            if self._context['auto_resume']:
                self._vim.command('autocmd denite WinEnter <buffer> ' +
                                  'Denite -resume -buffer_name=' +
                                  self._context['buffer_name'])
            for mapping in ['i', 'a', '<CR>']:
                self._vim.command(f'nnoremap <silent><buffer> {mapping} ' +
                                  ':<C-u>Denite -resume -buffer_name=' +
                                  f"{self._context['buffer_name']}<CR>")
        self._is_suspend = True
        self._options['modifiable'] = False
        return STATUS_ACCEPT
