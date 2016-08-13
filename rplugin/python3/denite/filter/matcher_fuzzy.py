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
        input = context['input']
        if input == '':
            return context['candidates']
        if context['ignorecase']:
            input = input.lower()
        p = re.compile(fuzzy_escape(input, True))
        if context['ignorecase']:
            return [x for x in context['candidates']
                    if p.search(x['word'].lower())]
        else:
            return [x for x in context['candidates']
                    if p.search(x['word'])]
