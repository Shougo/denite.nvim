# ============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re

from deoplete.base.source import Base
from deoplete.util import parse_buffer_pattern


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'denite'
        self.mark = '[denite]'
        self.filetypes = ['denite-filter']
        self.vars = {
            'enable_buffer_pattern': True,
        }

    def get_complete_position(self, context):
        if self.get_var('enable_buffer_pattern'):
            return super().get_complete_position(context)

        m = re.search(r'\S+$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        if self.get_var('enable_buffer_pattern'):
            candidates = sorted(parse_buffer_pattern(
                self.vim.vars['denite#_candidates'],
                context['keyword_pattern']), key=str.lower)
        else:
            candidates = self.vim.vars['denite#_candidates']
        return [{'word': x} for x in candidates]
