# ============================================================================
# FILE: sorter/word.py
# AUTHOR: Tomohito OZAKI <ozaki at yuroyoro.com>
# DESCRIPTION: Simple filter to sort candidates by ascii order of word
# License: MIT license
# ============================================================================

from denite.base.filter import Base


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'sorter/word'
        self.description = 'sort candidates by ascii order of word'

    def filter(self, context):
        return sorted(context['candidates'], key=lambda x: x['word'])
