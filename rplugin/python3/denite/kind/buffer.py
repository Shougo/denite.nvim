# ============================================================================
# FILE: buffer.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .openable import Kind as Openable


class Kind(Openable):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'buffer'
        self.default_action = 'open'
        self.redraw_actions += ['delete']
        self.persist_actions += ['delete']

    def action_open(self, context):
        for target in context['targets']:
            self.vim.command('buffer {0}'.format(target['action__bufnr']))

    def action_delete(self, context):
        for target in context['targets']:
            self.vim.call('denite#util#delete_buffer',
                          'bdelete', target['action__bufnr'])
