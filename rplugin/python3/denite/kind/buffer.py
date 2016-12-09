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

    def action_open(self, context):
        for target in context['targets']:
            self.vim.command('buffer {0}'.format(target['action__bufnr']))
