# ============================================================================
# FILE: source.py
# AUTHOR: Prabir Shrestha <mail at prabir.me>
# License: MIT license
# ============================================================================

from denite.base.source import Base
from denite.util import Nvim, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'source'
        self.kind = 'source'

    def gather_candidates(self, context: UserContext) -> Candidates:
        return [{'word': x, 'action__source': [x]} for x in
                self.vim.call('denite#helper#_get_available_sources')]
