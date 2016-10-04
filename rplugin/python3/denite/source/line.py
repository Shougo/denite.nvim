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
        context['__lines'] = self.vim.current.buffer[:]
        context['__buffer'] = self.vim.current.buffer.name

    def gather_candidates(self, context):
        lines = [{'word': x,
                  'action__path': context['__buffer'],
                  'action__line': (i + 1)}
                 for [i, x] in enumerate(context['__lines'])]
        return lines[context['__linenr']-1:] + lines[:context['__linenr']-1]
