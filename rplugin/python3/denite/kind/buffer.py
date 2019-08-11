# ============================================================================
# FILE: buffer.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from itertools import filterfalse
from denite.kind.openable import Kind as Openable
from denite.util import Nvim, UserContext, Candidate


class Kind(Openable):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'buffer'
        self.default_action = 'open'
        self.redraw_actions += ['delete']  # type: ignore
        self.persist_actions += ['delete', 'preview']  # type: ignore
        self._previewed_target: Candidate = {}

    def action_open(self, context: UserContext) -> None:
        for target in context['targets']:
            self.vim.command(f'buffer {target["action__bufnr"]}')

    def action_delete(self, context: UserContext) -> None:
        for target in context['targets']:
            self.vim.call('denite#util#delete_buffer',
                          'bdelete!', target['action__bufnr'])

    def action_preview(self, context: UserContext) -> None:
        target = context['targets'][0]

        if (context['auto_action'] != 'preview' and
                self._get_preview_window() and
                self._previewed_target == target):
            self.vim.command('pclose!')
            return

        prev_id = self.vim.call('win_getid')

        path = (target['action__path']
                if target['action__path'] else '[dummy]')
        self.vim.call('denite#helper#preview_file', context, path)
        self.vim.command('wincmd P')
        self.vim.current.window.options['foldenable'] = False

        self.action_open(context)
        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target

    def _get_preview_window(self) -> bool:
        return bool(next(filterfalse(
            lambda x: not x.options['previewwindow'],  # type: ignore
            self.vim.windows), None))

    # Needed for openable actions
    def _winid(self, target: Candidate) -> typing.Optional[int]:
        winids = self.vim.call('win_findbuf', target['action__bufnr'])
        return None if len(winids) == 0 else winids[0]
