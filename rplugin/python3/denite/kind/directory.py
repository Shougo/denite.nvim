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
        self.default_action = 'cd'

    def action_cd(self, context):
        target = context['targets'][0]
        # TODO want to narrow
        self.vim.command('lcd {}'.format(target['action__path']))

        if self.vim.current.buffer.options['filetype'] == 'vimshell':
            self.vim.command('VimShellCurrentDir')
        elif self.vim.call('exists', 't:deol'):
            self.vim.call('deol#cd', self.vim.call('getcwd'))

    def action_open(self, context):
        for target in context['targets']:
            path = target['action__path']
            match_path = '^{0}$'.format(path)

            if self.vim.call('bufwinnr', match_path) <= 0:
                self.vim.call(
                    'denite#util#execute_path', 'edit', path)
            elif self.vim.call('bufwinnr',
                               match_path) != self.vim.current.buffer:
                self.vim.call(
                    'denite#util#execute_path', 'buffer', path)

