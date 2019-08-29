# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
import typing

from denite.util import echo, error, regex_convert_py_vim, clearmatch
from denite.util import Nvim, UserContext, Candidates, Candidate
from denite.parent import SyncParent


class Default(object):
    @property
    def is_async(self) -> bool:
        return self._is_async

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim
        self._denite: typing.Optional[SyncParent] = None
        self._selected_candidates: typing.List[int] = []
        self._candidates: Candidates = []
        self._cursor = 0
        self._entire_len = 0
        self._result: typing.List[typing.Any] = []
        self._context: UserContext = {}
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
        self._displayed_texts: typing.List[str] = []
        self._statusline_sources = ''
        self._titlestring = ''
        self._ruler = False
        self._prev_action = ''
        self._prev_status: typing.Dict[str, typing.Any] = {}
        self._prev_curpos: typing.List[typing.Any] = []
        self._save_window_options: typing.Dict[str, typing.Any] = {}
        self._sources_history: typing.List[typing.Any] = []
        self._previous_text = ''
        self._floating = False
        self._updated = False
        self._timers: typing.Dict[str, int] = {}

    def start(self, sources: typing.List[typing.Any],
              context: UserContext) -> typing.List[typing.Any]:
        if not self._denite:
            # if hasattr(self._vim, 'run_coroutine'):
            #     self._denite = ASyncParent(self._vim)
            # else:
            self._denite = SyncParent(self._vim)

        self._result = []
        context['sources_queue'] = [sources]

        self._start_sources_queue(context)

        return self._result

    def do_action(self, action_name: str,
                  command: str = '', is_manual: bool = False) -> None:
        candidates = self._get_selected_candidates()
        if not self._denite or not candidates or not action_name:
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

            prev_cursor = self._cursor
            cursor_candidate = self._get_cursor_candidate()

            self._init_buffer()

            self.redraw(False)

            if cursor_candidate == self._get_candidate(prev_cursor):
                # Restore the cursor
                self._move_to_pos(prev_cursor)

            # Disable quit flag
            is_quit = False

        if not is_quit:
            self._selected_candidates = []
            self.redraw(action['is_redraw'])

        if is_manual and self._context['sources_queue']:
            self._context['input'] = ''
            self._context['quick_move'] = ''
            self._start_sources_queue(self._context)

        return

    def redraw(self, is_force: bool = True) -> None:
        self._context['is_redraw'] = is_force
        if is_force:
            self._gather_candidates()
        if self._update_candidates():
            self._update_buffer()
        else:
            self._update_status()
        self._context['is_redraw'] = False

    def quit(self) -> None:
        if self._denite:
            self._denite.on_close(self._context)
        self._quit_buffer()
        self._result = []
        return

    def _restart(self) -> None:
        self._context['input'] = ''
        self._quit_buffer()
        self._init_denite()
        self._gather_candidates()
        self._init_buffer()
        self._update_candidates()
        self._update_buffer()

    def _start_sources_queue(self, context: UserContext) -> None:
        if not context['sources_queue']:
            return

        self._sources_history.append({
            'sources': context['sources_queue'][0],
            'path': context['path'],
        })

        self._start(context['sources_queue'][0], context)

        if context['sources_queue']:
            context['sources_queue'].pop(0)
        context['path'] = self._context['path']

    def _start(self, sources: typing.List[typing.Any],
               context: UserContext) -> None:
        from denite.ui.map import do_map

        self._vim.command('silent! autocmd! denite')

        if re.search(r'\[Command Line\]$', self._vim.current.buffer.name):
            # Ignore command line window.
            return

        resume = self._initialized and context['resume']
        if resume:
            # Skip the initialization

            update = ('immediately', 'immediately_1',
                      'cursor_pos', 'prev_winid',
                      'start_filter', 'quick_move')
            for key in update:
                self._context[key] = context[key]

            self._check_move_option()
            if self._check_do_option():
                return

            self._init_buffer()
            if context['refresh']:
                self.redraw()
            self._move_to_pos(self._cursor)
        else:
            if self._context != context:
                self._context.clear()
                self._context.update(context)
            self._context['sources'] = sources
            self._context['is_redraw'] = False
            self._is_multi = len(sources) > 1

            if not sources:
                # Ignore empty sources.
                error(self._vim, 'Empty sources')
                return

            self._init_denite()
            self._gather_candidates()
            self._update_candidates()

            self._init_cursor()
            self._check_move_option()
            if self._check_do_option():
                return

            self._init_buffer()

        self._update_displayed_texts()
        self._update_buffer()
        self._move_to_pos(self._cursor)

        if self._context['quick_move'] and do_map(self, 'quick_move', []):
            return

        if self._context['start_filter']:
            do_map(self, 'open_filter_buffer', [])

    def _init_buffer(self) -> None:
        self._prev_status = dict()
        self._displayed_texts = []

        self._prev_bufnr = self._vim.current.buffer.number
        self._prev_curpos = self._vim.call('getcurpos')
        self._prev_wininfo = self._get_wininfo()
        self._prev_winid = int(self._context['prev_winid'])
        self._winrestcmd = self._vim.call('winrestcmd')

        self._ruler = self._vim.options['ruler']

        self._switch_buffer()
        self._bufnr = self._vim.current.buffer.number
        self._winid = self._vim.call('win_getid')

        self._resize_buffer()

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

        if self._floating:
            # Disable ruler
            self._vim.options['ruler'] = False

        self._window_options = self._vim.current.window.options
        window_options = {
            'colorcolumn': '',
            'concealcursor': 'inv',
            'conceallevel': 3,
            'cursorcolumn': False,
            'foldcolumn': 0,
            'foldenable': False,
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
        self._bufvars['denite'] = {
            'buffer_name': self._context['buffer_name'],
        }
        self._bufvars['denite_statusline'] = {}

        self._vim.vars['denite#_previewed_buffers'] = {}

        self._vim.command('silent doautocmd WinEnter')
        self._vim.command('silent doautocmd BufWinEnter')
        self._vim.command('doautocmd FileType denite')

        if self._context['auto_action']:
            self._vim.command('autocmd denite '
                              'CursorMoved <buffer> '
                              'call denite#call_map("auto_action")')

        self._init_syntax()

    def _switch_buffer(self) -> None:
        split = self._context['split']
        if (split != 'no' and self._winid > 0 and
                self._vim.call('win_gotoid', self._winid)):
            if split != 'vertical' and not self._floating:
                # Move the window to bottom
                self._vim.command('wincmd J')
            self._winrestcmd = ''
            return

        self._floating = False

        command = 'edit'
        if split == 'tab':
            self._vim.command('tabnew')
        elif (split == 'floating' and
                self._vim.call('exists', '*nvim_open_win')):
            if self._vim.current.buffer.options['filetype'] != 'denite':
                self._titlestring = self._vim.options['titlestring']
            # Use floating window
            self._floating = True
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
        bufname = '[denite]-' + self._context['buffer_name']
        if self._vim.call('exists', '*bufadd'):
            bufnr = self._vim.call('bufadd', bufname)
            vertical = 'vertical' if split == 'vertical' else ''
            command = ('buffer' if split in ['no', 'tab', 'floating']
                       else 'sbuffer')
            self._vim.command(
                'silent keepalt %s %s %s %s' % (
                    self._get_direction(),
                    vertical,
                    command,
                    bufnr,
                )
            )
        else:
            self._vim.call(
                'denite#util#execute_path',
                f'silent keepalt {command}', bufname)

    def _get_direction(self) -> str:
        direction = str(self._context['direction'])
        if direction == 'dynamictop' or direction == 'dynamicbottom':
            self._update_displayed_texts()
            winwidth = self._vim.call('winwidth', 0)
            is_fit = not [x for x in self._displayed_texts
                          if self._vim.call('strwidth', x) > winwidth]
            if direction == 'dynamictop':
                direction = 'aboveleft' if is_fit else 'topleft'
            else:
                direction = 'belowright' if is_fit else 'botright'
        return direction

    def _get_wininfo(self) -> typing.List[typing.Any]:
        return [
            self._vim.options['columns'], self._vim.options['lines'],
            self._vim.call('win_getid'), self._vim.call('tabpagebuflist')
        ]

    def _switch_prev_buffer(self) -> None:
        if (self._prev_bufnr == self._bufnr or
                self._vim.buffers[self._prev_bufnr].name == ''):
            self._vim.command('enew')
        else:
            self._vim.command('buffer ' + str(self._prev_bufnr))

    def _init_syntax(self) -> None:
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

        if self._floating:
            self._vim.current.window.options['winhighlight'] = (
                'Normal:' + self._context['highlight_window_background']
            )
        self._vim.command(('syntax match deniteSelectedLine /^[%s].*/' +
                           ' contains=deniteConcealedMark') % (
                               self._context['selected_icon']))
        self._vim.command(('syntax match deniteConcealedMark /^[ %s]/' +
                           ' conceal contained') % (
                               self._context['selected_icon']))

        if self._denite:
            self._denite.init_syntax(self._context, self._is_multi)

    def _update_candidates(self) -> bool:
        if not self._denite:
            return False

        [self._is_async, pattern, statuses, self._entire_len,
         self._candidates] = self._denite.filter_candidates(self._context)

        prev_displayed_texts = self._displayed_texts
        self._update_displayed_texts()

        prev_matched_pattern = self._matched_pattern
        self._matched_pattern = pattern

        prev_statusline_sources = self._statusline_sources
        self._statusline_sources = ' '.join(statuses)

        if self._is_async:
            self._start_timer('update_candidates')
        else:
            self._stop_timer('update_candidates')

        updated = (self._displayed_texts != prev_displayed_texts or
                   self._matched_pattern != prev_matched_pattern or
                   self._statusline_sources != prev_statusline_sources)
        if updated:
            self._updated = True
            self._start_timer('update_buffer')

        return self._updated

    def _update_displayed_texts(self) -> None:
        candidates_len = len(self._candidates)
        if not self._is_async and self._context['auto_resize']:
            winminheight = int(self._context['winminheight'])
            max_height = min(int(self._context['winheight']),
                             self._get_max_height())
            if (winminheight is not -1 and candidates_len < winminheight):
                self._winheight = winminheight
            elif candidates_len > max_height:
                self._winheight = max_height
            elif candidates_len != self._winheight:
                self._winheight = candidates_len

        max_source_name_len = 0
        if self._candidates:
            max_source_name_len = max([
                len(self._get_display_source_name(x['source_name']))
                for x in self._candidates])
        self._context['max_source_name_len'] = max_source_name_len
        self._context['max_source_name_format'] = (
            '{:<' + str(self._context['max_source_name_len']) + '}')
        self._displayed_texts = [
            self._get_candidate_display_text(i)
            for i in range(0, candidates_len)
        ]

    def _update_buffer(self) -> None:
        if self._bufnr != self._vim.current.buffer.number:
            return

        self._update_status()

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
        prev_candidate = self._get_cursor_candidate()

        self._options['modifiable'] = True
        self._vim.vars['denite#_candidates'] = [
            x['word'] for x in self._candidates]
        self._vim.current.buffer[:] = self._displayed_texts
        self._options['modifiable'] = False
        self._resize_buffer()

        self._vim.call('cursor', [prev_linenr, 0])

        if self._updated and (self._context['reversed'] or
                              self._previous_text != self._context['input']):
            self._previous_text = self._context['input']
            self._init_cursor()
            self._move_to_pos(self._cursor)

        if (self._context['auto_action'] and
                prev_candidate != self._get_cursor_candidate()):
            self.do_action(self._context['auto_action'])

        self._updated = False
        self._stop_timer('update_buffer')

    def _update_status(self) -> None:
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
            'line_total': len(self._candidates),
        }
        if status == self._prev_status:
            return

        self._bufvars['denite_statusline'] = status
        self._prev_status = status

        linenr = "printf('%'.(len(line('$'))+2).'d/%d',line('.'),line('$'))"

        if self._context['statusline']:
            if self._floating:
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

    def _get_display_source_name(self, name: str) -> str:
        source_names = self._context['source_names']
        if not self._is_multi or source_names == 'hide':
            source_name = ''
        else:
            short_name = (re.sub(r'([a-zA-Z])[a-zA-Z]+', r'\1', name)
                          if re.search(r'[^a-zA-Z]', name) else name[:2])
            source_name = short_name if source_names == 'short' else name
        return source_name

    def _get_candidate_display_text(self, index: int) -> str:
        source_names = self._context['source_names']
        candidate = self._candidates[index]
        terms = []
        if self._is_multi and source_names != 'hide':
            terms.append(self._context['max_source_name_format'].format(
                self._get_display_source_name(candidate['source_name'])))
        encoding = self._context['encoding']
        abbr = candidate.get('abbr', candidate['word']).encode(
            encoding, errors='replace').decode(encoding, errors='replace')
        terms.append(abbr[:int(self._context['max_candidate_width'])])
        return (self._context['selected_icon']  # type: ignore
                if index in self._selected_candidates
                else ' ') + ' '.join(terms).replace('\n', '')

    def _get_max_height(self) -> int:
        return int(self._vim.options['lines']) if not self._floating else (
            int(self._vim.options['lines']) -
            int(self._context['winrow']) -
            int(self._vim.options['cmdheight']))

    def _resize_buffer(self) -> None:
        split = self._context['split']
        if (split == 'no' or split == 'tab' or
                self._vim.call('winnr', '$') == 1):
            return

        winheight = max(self._winheight, 1)
        winwidth = max(self._winwidth, 1)
        is_vertical = split == 'vertical'

        if not is_vertical and self._vim.current.window.height != winheight:
            if self._floating:
                self._vim.call('nvim_win_set_config', self._winid, {
                    'relative': 'editor',
                    'row': int(self._context['winrow']),
                    'col': int(self._context['wincol']),
                    'width': winwidth,
                    'height': winheight,
                })

                filter_winid = self._vim.vars['denite#_filter_winid']
                if self._vim.call('win_id2win', filter_winid) > 0:
                    self._vim.call('nvim_win_set_config', filter_winid, {
                        'relative': 'editor',
                        'row': int(self._context['winrow']) + winheight,
                        'col': int(self._context['wincol']),
                    })

            self._vim.command('resize ' + str(winheight))
            if self._context['reversed']:
                self._vim.command('normal! zb')
        elif is_vertical and self._vim.current.window.width != winwidth:
            self._vim.command('vertical resize ' + str(winwidth))

    def _check_do_option(self) -> bool:
        if self._context['do'] != '':
            self._do_command(self._context['do'])
            return True
        elif (self._candidates and self._context['immediately'] or
                len(self._candidates) == 1 and self._context['immediately_1']):
            self._do_immediately()
            return True
        return not (self._context['empty'] or
                    self._is_async or self._candidates)

    def _check_move_option(self) -> None:
        if self._context['cursor_pos'].isnumeric():
            self._cursor = int(self._context['cursor_pos']) + 1
        elif re.match(r'\+\d+', self._context['cursor_pos']):
            for _ in range(int(self._context['cursor_pos'][1:])):
                self._move_to_next_line()
        elif re.match(r'-\d+', self._context['cursor_pos']):
            for _ in range(int(self._context['cursor_pos'][1:])):
                self._move_to_prev_line()
        elif self._context['cursor_pos'] == '$':
            self._move_to_last_line()

    def _do_immediately(self) -> None:
        goto = self._winid > 0 and self._vim.call(
            'win_gotoid', self._winid)
        if goto:
            # Jump to denite window
            self._init_buffer()
        self.do_action('default')
        candidate = self._get_cursor_candidate()
        if not candidate:
            return
        echo(self._vim, 'Normal', '[{}/{}] {}'.format(
            self._cursor, len(self._candidates),
            candidate.get('abbr', candidate['word'])))
        if goto:
            # Move to the previous window
            self._vim.command('wincmd p')

    def _do_command(self, command: str) -> None:
        self._init_cursor()
        cursor = 1
        while cursor < len(self._candidates):
            self.do_action('default', command)
            self._move_to_next_line()
        self._quit_buffer()

    def _cleanup(self) -> None:
        self._stop_timer('update_candidates')
        self._stop_timer('update_buffer')

        if self._vim.current.buffer.number == self._bufnr:
            self._cursor = self._vim.call('line', '.')
        # Clear previewed buffers
        if not self._context['has_preview_window']:
            self._vim.command('pclose!')
        for bufnr in self._vim.vars['denite#_previewed_buffers'].keys():
            if not self._vim.call('win_findbuf', bufnr):
                self._vim.command('silent bdelete ' + str(bufnr))
        self._vim.vars['denite#_previewed_buffers'] = {}

        self._vim.command('highlight! link CursorLine CursorLine')
        if self._floating:
            self._vim.options['titlestring'] = self._titlestring
            self._vim.options['ruler'] = self._ruler

    def _close_current_window(self) -> None:
        if self._vim.call('winnr', '$') == 1:
            self._vim.command('buffer #')
        else:
            self._vim.command('close!')

    def _quit_buffer(self) -> None:
        self._cleanup()
        if self._vim.call('bufwinnr', self._bufnr) < 0:
            # Denite buffer is already closed
            return

        winids = self._vim.call('win_findbuf',
                                self._vim.vars['denite#_filter_bufnr'])
        if winids:
            # Quit filter buffer
            self._vim.call('win_gotoid', winids[0])
            self._close_current_window()
            # Move to denite window
            self._vim.call('win_gotoid', self._winid)

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
                self._close_current_window()

            self._vim.call('win_gotoid', self._prev_winid)

        # Restore the position
        self._vim.call('setpos', '.', self._prev_curpos)

        if self._get_wininfo() and self._get_wininfo() == self._prev_wininfo:
            self._vim.command(self._winrestcmd)

        clearmatch(self._vim)

    def _get_cursor_candidate(self) -> Candidate:
        return self._get_candidate(self._cursor)

    def _get_candidate(self, pos: int) -> Candidate:
        if not self._candidates or pos > len(self._candidates):
            return {}
        return self._candidates[pos - 1]

    def _get_selected_candidates(self) -> Candidates:
        if not self._selected_candidates:
            return [self._get_cursor_candidate()
                    ] if self._get_cursor_candidate() else []
        return [self._candidates[x] for x in self._selected_candidates]

    def _init_denite(self) -> None:
        if self._denite:
            self._denite.start(self._context)
            self._denite.on_init(self._context)
        self._initialized = True
        self._winheight = int(self._context['winheight'])
        self._winwidth = int(self._context['winwidth'])

    def _gather_candidates(self) -> None:
        self._selected_candidates = []
        if self._denite:
            self._denite.gather_candidates(self._context)

    def _init_cursor(self) -> None:
        if self._context['reversed']:
            self._move_to_last_line()
            self._vim.command('normal! zb')
        else:
            self._move_to_first_line()

    def _move_to_pos(self, pos: int) -> None:
        self._vim.call('cursor', pos, 0)
        self._cursor = pos

    def _move_to_next_line(self) -> None:
        if self._cursor < len(self._candidates):
            self._cursor += 1

    def _move_to_prev_line(self) -> None:
        if self._cursor >= 1:
            self._cursor -= 1

    def _move_to_first_line(self) -> None:
        self._cursor = 1

    def _move_to_last_line(self) -> None:
        self._cursor = len(self._candidates)

    def _start_timer(self, key: str) -> None:
        if key in self._timers:
            return

        if key == 'update_candidates':
            self._timers[key] = self._vim.call(
                'denite#helper#_start_update_candidates_timer')
        elif key == 'update_buffer':
            self._timers[key] = self._vim.call(
                'denite#helper#_start_update_buffer_timer')

    def _stop_timer(self, key: str) -> None:
        if key not in self._timers:
            return

        self._vim.call('timer_stop', self._timers[key])
        self._timers.pop(key)
