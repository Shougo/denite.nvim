# ============================================================================
# FILE: converter/abbr_word.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.filter import Base
from denite.util import Nvim, UserContext, Candidates


class Filter(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'converter/abbr_word'
        self.description = 'convert candidate abbr to word'

    def filter(self, context: UserContext) -> Candidates:
        for candidate in context['candidates']:
            if 'abbr' in candidate:
                candidate['word'] = candidate['abbr']
        return context['candidates']  # type: ignore
