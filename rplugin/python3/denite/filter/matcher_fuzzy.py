# ============================================================================
# FILE: matcher_fuzzy.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
from .base import Base
from denite.util import fuzzy_escape


class Filter(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'matcher_fuzzy'
        self.description = 'fuzzy matcher'

    def filter(self, context):
        if context['input'] == '':
            return context['candidates']
        candidates = context['candidates']
        for pattern in re.split(r'\s+', context['input']):
            if context['ignorecase']:
                pattern = pattern.lower()
            p = re.compile(fuzzy_escape(pattern, True))
            if context['ignorecase']:
                candidates = [x for x in candidates
                              if p.search(x['word'].lower())]
            else:
                candidates = [x for x in candidates
                              if p.search(x['word'])]
        return candidates
