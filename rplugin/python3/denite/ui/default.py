# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import copy
import re

from denite.util import (
    clear_cmdline, echo, error, regex_convert_py_vim, clearmatch)
from denite.parent import SyncParent
from denite.ui.map import do_map


class Default(object):
    @property
    def is_async(self):
        return self._is_async

    def __init__(self, vim):
        self._vim = vim
        self._denite = None
        self._selected_candidates = []
        self._candidates = []
        self._candidates_len = 0
        self._result = []
        self._context = {}
        self._bufnr = -1
        self._winid = -1
        self._winrestcmd = ''
        self._initialized = False
        self._winheight = 0
        self._winwidth = 0
        self._winminheight = -1
        self._is_multi = False
        self._is_async = False
        self._matched_pattern = ''
        self._displayed_texts = []
        self._statusline_sources = ''
        self._titlestring = ''
        self._ruler = False
        self._prev_action = ''
        self._prev_status = {}
        self._prev_curpos = []
        self._save_window_options = {}
        self._sources_history = []
        self._previous_text = ''

    def start(self, sources, context):
        if not self._denite:
            self._denite = SyncParent(self._vim)
            # self._denite = ASyncParent(self._vim)

        self._result = []
        context['sources_queue'] = [sources]
        self._sources_history = []

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

        return self._result

    def _start(self, sources, context):
        self._vim.command('silent! autocmd! denite')

        if re.search(r'\[Command Line\]$', self._vim.current.buffer.name):
            # Ignore command line window.
            return

        if self._initialized and context['resume']:
            # Skip the initialization

            update = ('immediately', 'immediately_1',
                      'cursor_wrap', 'cursor_pos', 'prev_winid',
                      'quick_move')
            for key in update:
                self._context[key] = context[key]

            if self.check_do_option():
                return

            prev_linenr = self._vim.call('line', '.')

            self.init_buffer()
            if context['refresh']:
                self.redraw()

            self._vim.call('cursor', [prev_linenr, 0])
        else:
            self._context.clear()
            self._context.update(context)
            self._context['sources'] = sources
            self._context['is_redraw'] = False
            self._is_multi = len(sources) > 1

            if not sources:
                # Ignore empty sources.
                error(self._vim, 'Empty sources')
                return

            self.init_denite()
            self.gather_candidates()
            self.update_candidates()

            if self.check_do_option():
                return

            self.init_buffer()
            self.init_cursor()

        self.update_displayed_texts()
        self.update_buffer()
        self.check_move_option()

        if self._context['quick_move'] and self.quick_move():
            return

        if self._context['start_filter']:
            self.do_map('open_filter_buffer', [])

    def init_buffer(self):
        self._prev_status = dict()
        self._displayed_texts = []

        self._prev_bufnr = self._vim.current.buffer.number
        self._prev_curpos = self._vim.call('getcurpos')
        self._prev_wininfo = self._get_wininfo()
        self._prev_winid = int(self._context['prev_winid'])
        self._winrestcmd = self._vim.call('winrestcmd')

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
        self._options['modifiable'] = False

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

        self._bufvars['denite'] = {
            'buffer_name': self._context['buffer_name'],
        }
        self._bufvars['denite_statusline'] = {}

        self._vim.vars['denite#_previewed_buffers'] = {}

        self._vim.command('silent doautocmd WinEnter')
        self._vim.command('silent doautocmd BufWinEnter')
        self._vim.command('doautocmd FileType denite')
        self._vim.command('autocmd denite '
                          'CursorMoved <buffer> '
                          'call denite#call_map("auto_action")')
        self._vim.command('autocmd denite '
                          'CursorHold <buffer> '
                          'call denite#call_map("update")')

        self.init_syntax()

    def _switch_buffer(self):
        split = self._context['split']
        if (split != 'no' and self._winid > 0 and
                self._vim.call('win_gotoid', self._winid)):
            if split != 'vertical' and split != 'floating':
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
                self._vim.current.window.options['winhighlight'] = (
                  'Normal:' + self._context['highlight_window_background']
                )
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
        self._vim.command('highlight default link deniteInput ModeMsg')
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
        if self._context['reversed']:
            self.move_to_last_line()
        else:
            self.move_to_first_line()

    def update_candidates(self):
        [self._is_async, pattern, statuses,
         self._candidates] = self._denite.filter_candidates(self._context)

        prev_matched_pattern = self._matched_pattern
        self._matched_pattern = pattern
        self._candidates_len = len(self._candidates)

        self._statusline_sources = ' '.join(statuses)

        prev_displayed_texts = self._displayed_texts
        self.update_displayed_texts()

        updated = (self._displayed_texts != prev_displayed_texts or
                   self._matched_pattern != prev_matched_pattern)
        if updated and self._is_async and self._context['reversed']:
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
            for i in range(0, self._candidates_len)
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

        prev_linenr = self._vim.call('line', '.')

        self._options['modifiable'] = True
        self._vim.current.buffer[:] = self._displayed_texts
        self._options['modifiable'] = False
        self.resize_buffer()

        self._vim.call('cursor', [prev_linenr, 0])

        if self._context['auto_action']:
            self.do_action(self._context['auto_action'])

    def update_status(self):
        inpt = ''
        if self._context['input']:
            inpt = self._context['input'] + ' '
        if self._context['error_messages']:
            inpt = '[ERROR] ' + inpt
        path = '[' + self._context['path'] + ']'

        status = {
            'input': inpt,
            'sources': self._statusline_sources,
            'path': path,
            # Extra
            'buffer_name': self._context['buffer_name'],
            'line_total': self._candidates_len,
        }
        if status != self._prev_status:
            self._bufvars['denite_statusline'] = status
            self._vim.command('redrawstatus')
            self._prev_status = status

        linenr = "printf('%'.(len(line('$'))+2).'d/%d',line('.'),line('$'))"

        if self._context['statusline']:
            if self._context['split'] == 'floating':
                self._vim.options['titlestring'] = (
                    "%{denite#get_status('input')}%* " +
                    "%{denite#get_status('sources')} " +
                    " %{denite#get_status('path')}%*" +
                    "%{" + linenr + "}%*")
            else:
                self._window_options['statusline'] = (
                    "%#deniteInput#%{denite#get_status('input')}%* " +
                    "%{denite#get_status('sources')} %=" +
                    "%#deniteStatusLinePath# %{denite#get_status('path')}%*" +
                    "%#deniteStatusLineNumber#%{" + linenr + "}%*")

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

    def check_do_option(self):
        if self._context['do'] != '':
            self.do_command(self._context['do'])
            return True
        elif (self._candidates and self._context['immediately'] or
                len(self._candidates) == 1 and self._context['immediately_1']):
            self.do_immediately()
            return True
        return not (self._context['empty'] or
                    self._is_async or self._candidates)

    def check_move_option(self):
        if self._context['cursor_pos'].isnumeric():
            self.move_to_pos(int(self._context['cursor_pos']) + 1)
        elif re.match(r'\+\d+', self._context['cursor_pos']):
            for _ in range(int(self._context['cursor_pos'][1:])):
                self.move_to_next_line()
        elif re.match(r'-\d+', self._context['cursor_pos']):
            for _ in range(int(self._context['cursor_pos'][1:])):
                self.move_to_prev_line()
        elif self._context['cursor_pos'] == '$':
            self.move_to_last_line()

    def do_immediately(self):
        goto = self._winid > 0 and self._vim.call(
            'win_gotoid', self._winid)
        if goto:
            # Jump to denite window
            self.init_buffer()
        self.do_action('default')
        candidate = self.get_cursor_candidate()
        echo(self._vim, 'Normal', '[{}/{}] {}'.format(
            self._vim.call('line', '.'), self._candidates_len,
            candidate.get('abbr', candidate['word'])))
        if goto:
            # Move to the previous window
            self._vim.command('wincmd p')

    def do_command(self, command):
        self.init_cursor()
        cursor = 1
        while cursor < self._candidates_len:
            self.do_action('default', command)
            self.move_to_next_line()
        self.quit_buffer()

    def cleanup(self):
        # Clear previewed buffers
        if not self._context['has_preview_window']:
            self._vim.command('pclose!')
        for bufnr in self._vim.vars['denite#_previewed_buffers'].keys():
            if not self._vim.call('win_findbuf', bufnr):
                self._vim.command('silent bdelete ' + str(bufnr))
        self._vim.vars['denite#_previewed_buffers'] = {}

        self._vim.command('highlight! link CursorLine CursorLine')
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

        clearmatch(self._vim)

    def get_cursor_candidate(self):
        cursor = self._vim.call('line', '.')
        if cursor > self._candidates_len:
            return {}
        return self._candidates[cursor - 1]

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
        return

    def restart(self):
        self.quit_buffer()
        self.init_denite()
        self.gather_candidates()
        self.init_buffer()
        self.update_candidates()
        self.update_buffer()

    def restore_sources(self, context):
        if not self._sources_history:
            return

        history = self._sources_history[-1]
        context['sources_queue'].append(history['sources'])
        context['path'] = history['path']
        self._sources_history.pop()
        return

    def init_denite(self):
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
            return

        post_action = self._context['post_action']

        is_quit = action['is_quit'] or post_action == 'quit'
        if is_quit:
            self.quit()

        self._denite.do_action(self._context, action_name, candidates)
        self._result = candidates
        if command != '':
            self._vim.command(command)

        if is_quit and post_action == 'open':
            # Re-open denite buffer

            self.init_buffer()

            self.redraw(False)
            # Disable quit flag
            is_quit = False

        if not is_quit:
            self._selected_candidates = []
            self.redraw(action['is_redraw'])

        return

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

    def do_map(self, name, args):
        return do_map(self, name, args)

    def move_to_pos(self, pos):
        self._vim.call('cursor', pos, 0)

    def move_to_next_line(self):
        cursor = self._vim.call('line', '.')
        if cursor < self._candidates_len:
            cursor += 1
        elif self._context['cursor_wrap']:
            self.move_to_first_line()
        else:
            return
        self._vim.call('cursor', cursor, 0)

    def move_to_prev_line(self):
        cursor = self._vim.call('line', '.')
        if cursor >= 1:
            cursor -= 1
        elif self._context['cursor_wrap']:
            self.move_to_last_line()
        else:
            return
        self._vim.call('cursor', cursor, 0)

    def move_to_first_line(self):
        self._vim.call('cursor', 1, 0)

    def move_to_last_line(self):
        self._vim.call('cursor', 1, self._vim.call('line', '$'))

    def quick_move(self):
        def get_quick_move_table():
            table = {}
            context = self._context
            base = self._vim.call('winline')
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

        for _ in range(int(quick_move_table[char]) - 1):
            self.move_to_next_line()

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
