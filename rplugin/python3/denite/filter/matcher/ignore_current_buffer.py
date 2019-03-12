# ============================================================================
# FILE: matcher/ignore_current_buffer.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.filter import Base


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher/ignore_current_buffer'
        self.description = 'ignore the current buffer path'

    def filter(self, context):
        current_buffer = self.vim.call(
            'fnamemodify', self.vim.buffers[int(context['bufnr'])].name, ':p')
        return [x for x in context['candidates']
                if 'action__path' not in x or
                x['action__path'] != current_buffer]
