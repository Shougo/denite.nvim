# ============================================================================
# FILE: converter/relative_abbr.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from os.path import isabs

from denite.base.filter import Base
from denite.util import relpath


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'converter/relative_abbr'
        self.description = 'convert candidate abbr to relative path'

    def filter(self, context):
        for candidate in context['candidates']:
            if isabs(candidate['word']):
                candidate['abbr'] = relpath(
                    self.vim,
                    candidate.get('action__path', candidate['word']))
        return context['candidates']
