# ============================================================================
# FILE: source.py
# AUTHOR: Prabir Shrestha <mail at prabir.me>
# License: MIT license
# ============================================================================

from denite.source.base import Base
from denite.kind.base import Base as BaseKind


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'source'
        self.kind = Kind(vim)

    def gather_candidates(self, context):
        return [{'word': x, 'action__source': x} for x in
                self.vim.call('denite#helper#_get_available_sources')]


class Kind(BaseKind):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'source'
        self.default_action = 'start'

    def action_start(self, context):
        context['sources_queue'].append([
            {'name': x['action__source'], 'args': []}
            for x in context['targets']
        ])
