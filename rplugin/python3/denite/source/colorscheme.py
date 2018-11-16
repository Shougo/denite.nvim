# ============================================================================
# FILE: colorscheme.py
# AUTHOR: Prabir Shrestha <mail at prabir.me>
# License: MIT license
# ============================================================================

from os import path

from denite.source.base import Base
from denite.util import globruntime


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'colorscheme'
        self.kind = 'colorscheme'

    def on_init(self, context):
        context['currentColor'] = self.vim.vars['colors_name']


    def on_close(self, context):
        self.vim.command('silent colorscheme {}'.format(context['currentColor']))

    def gather_candidates(self, context):
        colorschemes = {}

        for filename in globruntime(context['runtimepath'], 'colors/*.vim'):
            colorscheme = path.splitext(path.basename(filename))[0]
            colorschemes[colorscheme] = {
                'word': colorscheme,
                'action__command': 'colorscheme ' + colorscheme
            }

        return sorted(colorschemes.values(), key=lambda value: value['word'])
