# ============================================================================
# FILE: matcher/hide_hidden_files.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from os.path import basename
from re import match

from denite.base.filter import Base


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher/hide_hidden_files'
        self.description = 'hide the hidden files'

    def filter(self, context):
        if '.' in context['input']:
            return context['candidates']

        return [x for x in context['candidates']
                if not match(r'\.', basename(x['action__path']))]
