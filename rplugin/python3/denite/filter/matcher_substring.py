# ============================================================================
# FILE: matcher_substring.py
# AUTHOR: Andrew Ruder <andy at aeruder.net>
# License: MIT license
# ============================================================================

import re
from .base import Base
from denite.util import split_input

class Filter(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher_substring'
        self.description = 'simple substring matcher'

    def filter(self, context):
        candidates = context['candidates']
        ignorecase = context['ignorecase']
        if context['input'] == '':
            return candidates
        max_width = context['max_candidate_width']
        for pattern in split_input(context['input']):
            if ignorecase:
                pattern = pattern.lower()
                candidates = [x for x in candidates
                              if pattern in x['word'][:max_width].lower()]
            else:
                candidates = [x for x in candidates
                              if pattern in x['word'][:max_width]]
        return candidates

    def convert_pattern(self, input_str):
        return '\|'.join([re.escape(x) for x in split_input(input_str)])
