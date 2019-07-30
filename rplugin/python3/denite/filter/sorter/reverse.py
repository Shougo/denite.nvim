# ============================================================================
# FILE: sorter/reverse.py
# AUTHOR: Jacob Niehus <jacob.niehus at gmail.com>
# DESCRIPTION: Simple filter to reverse the order of candidates
# License: MIT license
# ============================================================================

from denite.base.filter import Base
from denite.util import Nvim, UserContext, Candidates


class Filter(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'sorter/reverse'
        self.description = 'reverse order of candidates'

    def filter(self, context: UserContext) -> Candidates:
        return list(reversed(context['candidates']))
