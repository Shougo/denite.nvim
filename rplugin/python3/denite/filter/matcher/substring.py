# ============================================================================
# FILE: matcher/substring.py
# AUTHOR: Andrew Ruder <andy at aeruder.net>
# License: MIT license
# ============================================================================

import re

from denite.base.filter import Base
from denite.util import split_input, Nvim, UserContext, Candidates


class Filter(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'matcher/substring'
        self.description = 'simple substring matcher'

    def filter(self, context: UserContext) -> Candidates:
        candidates: Candidates = context['candidates']
        ignorecase = context['ignorecase']
        if context['input'] == '':
            return candidates

        pattern = context['input']
        if ignorecase:
            pattern = pattern.lower()
            candidates = [x for x in candidates
                          if pattern in x['word'].lower()]
        else:
            candidates = [x for x in candidates if pattern in x['word']]
        return candidates

    def convert_pattern(self, input_str: str) -> str:
        return '|'.join([re.escape(x) for x in split_input(input_str)])
