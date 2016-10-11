# ============================================================================
# FILE: directory.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         okamos <himinato.k at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'directory'

    def action_default(self, context):
        target = context['targets'][0]
        # TODO want to narrow
        self.vim.command('cd {}'.format(target['action__path']))

        if self.vim.current.buffer.options['filetype'] == 'vimshell':
            # Change vimshell current directory
            self.vim.command('VimShellCurrentDir')
