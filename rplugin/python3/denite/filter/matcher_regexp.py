# ============================================================================
# FILE: matcher_regexp.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
from .base import Base


class Filter(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'matcher_regexp'
        self.description = 'regexp matcher'

    def filter(self, context):
        if context['input'] == '':
            return context['candidates']
        candidates = context['candidates']
        for pattern in re.split(r'\s+', context['input']):
            if context['ignorecase']:
                p = re.compile(pattern, re.IGNORECASE)
            else:
                p = re.compile(pattern)
            candidates = [x for x in candidates if p.search(x['word'])]
        return candidates
