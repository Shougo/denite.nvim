# ============================================================================
# FILE: source.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.kind import Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'source'
        self.default_action = 'start'

    def action_start(self, context):
        context['sources_queue'].append([{
            'name': x['action__source'][0],
            'args': x['action__source'][1:]
        } for x in context['targets']])
