# ============================================================================
# FILE: sorter_reverse.py
# AUTHOR: Jacob Niehus <jacob.niehus at gmail.com>
# DESCRIPTION: Simple filter to reverse the order of candidates
# License: MIT license
# ============================================================================
from .base import Base


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'sorter_reverse'
        self.description = 'reverse order of candidates'

    def filter(self, context):
        return list(reversed(context['candidates']))
