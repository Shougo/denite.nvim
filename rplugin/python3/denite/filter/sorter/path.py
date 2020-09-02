# ============================================================================
# FILE: sorter/path.py
# AUTHOR: uplus <uplus.e10 at gmail.com>
# DESCRIPTION: Simple filter to sort candidates by ascii order of path
# License: MIT license
# ============================================================================

from denite.base.filter import Base
from denite.util import Nvim, UserContext, Candidates


class Filter(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'sorter/path'
        self.description = 'sort candidates by ascii order of path'

    def filter(self, context: UserContext) -> Candidates:
        return sorted(context['candidates'], key=lambda x: x['action__path'])
