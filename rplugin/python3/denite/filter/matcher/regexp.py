# ============================================================================
# FILE: matcher/regexp.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re

from denite.base.filter import Base
from denite.util import convert2regex_pattern


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher/regexp'
        self.description = 'regexp matcher'

    def filter(self, context):
        if context['input'] == '':
            return context['candidates']
        candidates = context['candidates']
        try:
            p = re.compile(context['input'], flags=re.IGNORECASE
                           if context['ignorecase'] else 0)
        except Exception:
            return []
        candidates = [x for x in candidates if p.search(x['word'])]
        return candidates

    def convert_pattern(self, input_str):
        return convert2regex_pattern(input_str)
