# ============================================================================
# FILE: source.py
# AUTHOR: Prabir Shrestha <mail at prabir.me>
# License: MIT license
# ============================================================================

from denite.base.source import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'source'
        self.kind = 'source'

    def gather_candidates(self, context):
        return [{'word': x, 'action__source': [x]} for x in
                self.vim.call('denite#helper#_get_available_sources')]
