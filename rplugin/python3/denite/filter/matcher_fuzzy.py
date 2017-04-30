# ============================================================================
# FILE: matcher_fuzzy.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
from .base import Base
from denite.util import escape_fuzzy, split_input, convert2fuzzy_pattern


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher_fuzzy'
        self.description = 'fuzzy matcher'

    def filter(self, context):
        if context['input'] == '':
            return context['candidates']
        candidates = context['candidates']
        for pattern in split_input(context['input']):
            if context['ignorecase']:
                pattern = pattern.lower()
            p = re.compile(escape_fuzzy(re.escape(pattern), True))
            if context['ignorecase']:
                candidates = [x for x in candidates
                              if p.search(x['word'].lower())]
            else:
                candidates = [x for x in candidates if p.search(x['word'])]
        return candidates

    def convert_pattern(self, input_str):
        return convert2fuzzy_pattern(input_str)
