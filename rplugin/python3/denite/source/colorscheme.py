# ============================================================================
# FILE: colorscheme.py
# AUTHOR: Prabir Shrestha <mail at prabir.me>
# License: MIT license
# ============================================================================

from os import path

from denite.base.source import Base
from denite.kind.command import Kind as Command

from denite.util import globruntime


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'colorscheme'
        self.kind = Kind(vim)

    def on_init(self, context):
        context['__current_color'] = self.vim.vars.get(
            'colors_name', 'default')

    def on_close(self, context):
        self.vim.command(
            f'silent colorscheme {context["__current_color"]}')

    def gather_candidates(self, context):
        colorschemes = {}

        for filename in globruntime(context['runtimepath'], 'colors/*.vim'):
            colorscheme = path.splitext(path.basename(filename))[0]
            colorschemes[colorscheme] = {
                'word': colorscheme,
                'action__command': 'colorscheme ' + colorscheme
            }

        return sorted(colorschemes.values(), key=lambda value: value['word'])


class Kind(Command):
    def __init__(self, vim):
        super().__init__(vim)
        self.vim = vim
        self.name = 'colorscheme'

    def action_preview(self, context):
        target = context['targets'][0]
        self.vim.command(f'silent colorscheme {target["word"]}')
