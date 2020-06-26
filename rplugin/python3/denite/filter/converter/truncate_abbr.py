# ============================================================================
# FILE: converter/truncate_abbr.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path

from denite.base.filter import Base
from denite.util import Nvim, UserContext, Candidates, truncate


class Filter(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'converter/truncate_abbr'
        self.description = 'truncate candidate abbr by winwidth'

    def filter(self, context: UserContext) -> Candidates:
        for candidate in context['candidates']:
            if 'abbr' not in candidate:
                candidate['abbr'] = candidate['word']
            candidate['abbr'] = truncate(
                self.vim, candidate['abbr'], context['winwidth'])
        return context['candidates']  # type: ignore
