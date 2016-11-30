# ============================================================================
# FILE: line.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'line'
        self.kind = 'file'
        self.matchers = ['matcher_regexp']
        self.sorters = []

    def on_init(self, context):
        context['__linenr'] = self.vim.current.window.cursor[0]
        context['__bufname'] = self.vim.current.buffer.name
        context['__bufnr'] = self.vim.current.buffer.number

    def gather_candidates(self, context):
        lines = [{'word': x,
                  'action__path': context['__bufname'],
                  'action__line': (i + 1)}
                 for [i, x] in
                 enumerate(self.vim.call(
                     'getbufline', context['__bufnr'], 1, '$'))]
        return lines[context['__linenr']-1:] + lines[:context['__linenr']-1]
