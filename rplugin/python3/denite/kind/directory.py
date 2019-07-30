# ============================================================================
# FILE: directory.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         okamos <himinato.k at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.kind import Base
from denite.util import Nvim, UserContext


class Kind(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'directory'
        self.default_action = 'narrow'

    def action_cd(self, context: UserContext) -> None:
        target = context['targets'][0]
        self.vim.call('denite#util#cd', target['action__path'])

    def action_narrow(self, context: UserContext) -> None:
        target = context['targets'][0]
        context['sources_queue'].append([
            {'name': 'file', 'args': []},
            {'name': 'file', 'args': ['new']},
        ])
        context['path'] = target['action__path']

    def action_open(self, context: UserContext) -> None:
        for target in context['targets']:
            path = target['action__path']
            match_path = f'^{path}$'

            if self.vim.call('bufwinnr', match_path) <= 0:
                self.vim.call(
                    'denite#util#execute_path', 'edit', path)
            elif self.vim.call('bufwinnr',
                               match_path) != self.vim.current.buffer:
                self.vim.call(
                    'denite#util#execute_path', 'buffer', path)
