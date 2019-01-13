# ============================================================================
# FILE: matcher/expand.py
# AUTHOR: JINNOUCHI Yasushi <delphinus@remora.cx>
# License: MIT license
# ============================================================================

import re

from denite.filter.base import Base
from denite.util import expand, split_input


class Filter(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher/expand'
        self.description = 'expand `~` char & any env variable'

    def filter(self, context):
        candidates = context['candidates']
        ignorecase = context['ignorecase']
        pattern = context['input']
        if pattern == '':
            return candidates

        expanded = expand(pattern)
        if ignorecase:
            candidates = [x for x in candidates
                          if expanded.lower() in x['word'].lower()]
        else:
            candidates = [x for x in candidates if expanded in x['word']]
        return candidates

    def convert_pattern(self, input_str):
        return '|'.join([re.escape(expand(x)) for x in split_input(input_str)])
