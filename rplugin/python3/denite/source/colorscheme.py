# ============================================================================
# FILE: colorscheme.py
# AUTHOR: Prabir Shrestha <mail at prabir.me>
# License: MIT license
# ============================================================================

from .base import Base
from os import path
from denite.util import globruntime


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'colorscheme'
        self.kind = 'command'

    def gather_candidates(self, context):
        colorschemes = {}

        for file in globruntime(context['runtimepath'], 'colors/*.vim'):
            colorscheme = path.splitext(path.basename(file))[0]
            colorschemes[colorscheme] = {
                'word': colorscheme,
                'action__command': 'colorscheme ' + colorscheme
            }

        return sorted(colorschemes.values(), key=lambda value: value['word'])
