# ============================================================================
# FILE: sorter/rank.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# CONTRIBUTOR: Tristan Konolige
# DESCRIPTION: Sorter that does no sorting
# License: MIT license
# ============================================================================

from denite.base.filter import Base


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'sorter/none'
        self.description = 'no sorting'

    def filter(self, context):
        return context['candidates']
