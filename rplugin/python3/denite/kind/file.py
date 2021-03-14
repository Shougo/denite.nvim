# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
from pynvim import Nvim
import re
import typing

from denite.kind.openable import Kind as Openable
from denite.util import UserContext, Candidate
from denite import util


class Kind(Openable):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self._vim = vim
        self.name = 'file'
        self.default_action = 'open'
        self.persist_actions += ['highlight', 'preview_bat']
        self._previewed_target: typing.Dict[str, Candidate] = {}

    def action_open(self, context: UserContext) -> None:
        self._open(context, 'edit')

    def action_drop(self, context: UserContext) -> None:
        self._open(context, 'drop')

    def action_new(self, context: UserContext) -> None:
        path = str(self.vim.call('denite#util#input',
                                 'New file: ',
                                 '',
                                 'file'))
        if not path:
            return
        context['targets'] = [{
            'word': path,
            'action__path': util.abspath(self.vim, path),
        }]
        self.action_open(context)

    def action_preview(self, context: UserContext) -> None:
        target = context['targets'][0]

        if (self._previewed_target == target and
                context['auto_action'] == 'preview'):
            # Skip if auto_action
            return

        if (self._get_preview_window() and
                self._previewed_target == target):
            # Close the window only
            self.vim.command('pclose!')
            return

        if 'action__bufnr' in target:
            listed = self.vim.call('buflisted', target['action__bufnr'])
            path = self.vim.call('bufname', target['action__bufnr'])
        else:
            listed = self.vim.call('buflisted', target['action__path'])
            path = target['action__path'].replace('/./', '/')
        prev_id = self.vim.call('win_getid')

        self.vim.call('denite#helper#preview_file', context, path)
        self.vim.command('wincmd P')
        self.vim.current.window.options['foldenable'] = False

        if not listed:
            self._add_previewed_buffer(self.vim.call('bufnr', '%'))
        self._jump(context, target)
        self._highlight(context, target)

        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target

    def action_preview_bat(self, context: UserContext) -> None:
        target = context['targets'][0]

        if not self.vim.call('executable', 'bat'):
            return

        if 'action__bufnr' in target:
            path = self.vim.call('bufname', target['action__bufnr'])
        else:
            path = target['action__path'].replace('/./', '/')

        bat_cmd = ['bat', '-n', path]
        line = int(target.get('action__line', 0))
        if line:
            start_line = max(0, line - int(context['preview_height'] / 2))
            bat_cmd.extend(['-r', '{}:'.format(start_line),
                            '--highlight-line', line])

        self.preview_terminal(context, bat_cmd, 'preview_bat')

    def action_highlight(self, context: UserContext) -> None:
        target = context['targets'][0]
        if 'action__bufnr' in target:
            bufnr = target['action__bufnr']
        else:
            bufnr = self.vim.call('bufnr', target['action__path'])

        if not (self.vim.call('win_id2win', context['prev_winid']) and
                context['prev_winid'] in self.vim.call('win_findbuf', bufnr)):
            return

        prev_id = self.vim.call('win_getid')
        self.vim.call('win_gotoid', context['prev_winid'])
        self._jump(context, target)
        self._highlight(context, target)
        self.vim.call('win_gotoid', prev_id)

    def action_quickfix(self, context: UserContext) -> None:
        self._qfloc(context, 'qf')

    def action_location(self, context: UserContext) -> None:
        self._qfloc(context, 'loc')

    def _qfloc(self, context: UserContext, listtype: str) -> None:
        qfloclist = []
        for target in [x for x in context['targets']
                       if 'action__line' in x and 'action__text' in x]:
            qfloc = {
                'lnum': target['action__line'],
                'col': target['action__col'],
                'text': target['action__text'],
            }
            if 'action__bufnr' in target:
                qfloc['bufnr'] = target['action__bufnr']
            else:
                qfloc['filename'] = target['action__path']
            qfloclist.append(qfloc)
        if listtype == 'qf':
            self.vim.call('setqflist', qfloclist)
            self.vim.command('copen')
        if listtype == 'loc':
            wininfo = self._vim.call('denite#helper#_get_wininfo')
            self.vim.call('setloclist', wininfo['winnr'], qfloclist)
            self.vim.command('lopen')

    def _open(self, context: UserContext, command: str) -> None:
        for target in context['targets']:
            if 'action__bufnr' in target:
                bufnr = target['action__bufnr']
                self.vim.command('buffer' + str(bufnr))
            else:
                path = target['action__path']
                match_path = f'^{path}$'

                if re.match('https?://', path):
                    # URI
                    self.vim.call('denite#util#open', path)
                    continue
                cwd = self.vim.call('getcwd')
                if path.startswith(cwd):
                    path = str(Path(path).relative_to(cwd))

                bufnr = self.vim.call('bufnr', match_path)
                if (command == 'edit' and bufnr > 0 and
                        self.vim.call('buflisted', bufnr)):
                    self.vim.command('buffer' + str(bufnr))
                else:
                    self.vim.call(
                        'denite#util#execute_path', command, path)

            self._remove_previewed_buffer(bufnr)
            self._jump(context, target)

    def _highlight(self, context: UserContext, target: Candidate) -> None:
        util.clearmatch(self.vim)
        if 'action__pattern' in target:
            self.vim.current.window.vars['denite_match_id'] = self.vim.call(
                'matchadd', context['highlight_preview_line'],
                target['action__pattern'])
        else:
            line = int(target.get('action__line', 0))
            self.vim.current.window.vars['denite_match_id'] = self.vim.call(
                'matchaddpos', context['highlight_preview_line'], [line])

    def _get_preview_window(self) -> bool:
        return bool(self._vim.call('denite#helper#_get_preview_window'))

    # Needed for openable actions
    def _winid(self, target: Candidate) -> typing.Optional[int]:
        if 'action__bufnr' in target:
            bufnr = target['action__bufnr']
        else:
            path = target['action__path']
            bufnr = self.vim.call('bufnr', path)
        if bufnr == -1:
            return None
        winids = self.vim.call('win_findbuf', bufnr)
        return None if len(winids) == 0 else winids[0]

    def _add_previewed_buffer(self, bufnr: int) -> None:
        previewed_buffers = self._vim.vars['denite#_previewed_buffers']
        previewed_buffers[str(bufnr)] = 1
        self._vim.vars['denite#_previewed_buffers'] = previewed_buffers

    def _remove_previewed_buffer(self, bufnr: int) -> None:
        previewed_buffers = self._vim.vars['denite#_previewed_buffers']
        if str(bufnr) in previewed_buffers:
            previewed_buffers.pop(str(bufnr))
        self._vim.vars['denite#_previewed_buffers'] = previewed_buffers
