# ============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from deoplete.base.source import Base
from deoplete.util import parse_buffer_pattern


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'denite'
        self.mark = '[denite]'
        self.filetypes = ['denite-filter']

    def gather_candidates(self, context):
        return [{'word': x} for x in
                sorted(parse_buffer_pattern(
                    self.vim.vars['denite#_candidates'],
                    context['keyword_pattern']), key=str.lower)]
