# ============================================================================
# FILE: line.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'line'
        self.kind = 'jump_list'

    def on_init(self, context):
        context['__lines'] = self.vim.current.buffer[:]
        context['__buffer'] = self.vim.current.buffer.name

    def gather_candidates(self, context):
        return [{'word': x,
                 'action__path': context['__buffer'],
                 'action__line': (i + 1)}
                for [i, x] in enumerate(context['__lines'])]
