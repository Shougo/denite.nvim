# ============================================================================
# FILE: action.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.source import Base
from denite.base.kind import Kind as KindBase
from denite.util import Nvim, UserContext, Candidates


class Source(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.vim = vim
        self.name = '_action'
        self.kind = Kind(vim)
        self.default_action = 'do'

    def gather_candidates(self, context: UserContext) -> Candidates:
        if len(context['args']) < 3:
            return []

        candidates: Candidates = []
        actions = context['args'][0]
        candidates = [
            {
                'word': x,
                'action__buffer_name': context['args'][1],
                'action__targets': context['args'][2],
            } for x in actions
        ]
        return candidates

    def get_status(self, context: UserContext) -> str:
        return self.name


class Kind(KindBase):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'action'

    def action_do(self, context: UserContext) -> None:
        context['next_actions'] = [
            {
                'name': x['word'],
                'targets': x['action__targets'],
                'buffer_name': x['action__buffer_name'],
            } for x in context['targets']
        ]
