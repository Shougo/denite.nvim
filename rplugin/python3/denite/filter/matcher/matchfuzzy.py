# ============================================================================
# FILE: matcher/matchfuzzy.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.filter import Base
from denite.util import convert2fuzzy_pattern
from denite.util import Nvim, UserContext, Candidates


class Filter(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'matcher/matchfuzzy'
        self.description = 'matchfuzzy matcher'

    def filter(self, context: UserContext) -> Candidates:
        if (context['input'] == '' or not self.vim.call(
                                        'exists', '*matchfuzzy')):
            return list(context['candidates'])

        return list(self.vim.call(
                        'matchfuzzy', context['candidates'],
                        context['complete_str'], {'key': 'word'}
                ))

    def convert_pattern(self, input_str: str) -> str:
        return convert2fuzzy_pattern(input_str)
