# ============================================================================
# FILE: converter_relative_word.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from os.path import relpath, isabs


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'converter_relative_word'
        self.description = 'convert candidate word to relative path'

    def filter(self, context):
        for candidate in context['candidates']:
            if isabs(candidate['word']):
                candidate['word'] = relpath(
                    candidate['word'], start=context['path'])
        return context['candidates']
