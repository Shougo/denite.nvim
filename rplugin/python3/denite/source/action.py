# ============================================================================
# FILE: action.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.source import Base
from denite.util import Nvim, UserContext, Candidates


class Source(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.vim = vim
        self.name = '_action'

    def gather_candidates(self, context: UserContext) -> Candidates:
        candidates: Candidates = []
        actions = context['args'][0]
        self.debug(context['args'][1])
        candidates = [
            {'word': x} for x in actions
        ]
        return candidates
