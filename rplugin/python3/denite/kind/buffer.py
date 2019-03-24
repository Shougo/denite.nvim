# ============================================================================
# FILE: buffer.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from itertools import filterfalse
from denite.kind.openable import Kind as Openable


class Kind(Openable):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'buffer'
        self.default_action = 'open'
        self.redraw_actions += ['delete']
        self.persist_actions += ['delete', 'preview']
        self._previewed_target = {}

    def action_open(self, context):
        for target in context['targets']:
            self.vim.command(f'buffer {target["action__bufnr"]}')

    def action_delete(self, context):
        for target in context['targets']:
            self.vim.call('denite#util#delete_buffer',
                          'bdelete!', target['action__bufnr'])

    def action_preview(self, context):
        target = context['targets'][0]

        if (context['auto_action'] != 'preview' and
                self._get_preview_window() and
                self._previewed_target == target):
            self.vim.command('pclose!')
            return

        prev_id = self.vim.call('win_getid')
        self.vim.command('pedit!')
        self.vim.command('wincmd P')
        self.action_open(context)
        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target

    def _get_preview_window(self):
        return next(filterfalse(lambda x:
                                not x.options['previewwindow'],
                                self.vim.windows), None)

    # Needed for openable actions
    def _winid(self, target):
        winids = self.vim.call('win_findbuf', target['action__bufnr'])
        return None if len(winids) == 0 else winids[0]
