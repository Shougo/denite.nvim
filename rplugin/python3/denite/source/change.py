# ============================================================================
# FILE: change.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base

import re


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'change'
        self.kind = 'file'

    def on_init(self, context):
        context['__parse'] = self._parse(context)

    def _parse(self, context):
        changes = []
        for change in self.vim.call('execute', 'changes').split('\n'):
            texts = change.split()
            if len(texts) < 4 or not re.search('^\d+$', texts[1]):
                continue

            [linenr, col, text] = [
                int(texts[1]), int(texts[2]) + 1, ' '.join(texts[3:])]

            changes.append({
                'word': '%4d-%-3d  %s' % (linenr, col, text),
                'action__path': self.vim.call(
                    'fnamemodify', self.vim.call('bufname', '%'), ':p'),
                'action__line': linenr,
                'action__col': col,
            })
        return list(reversed(changes))

    def gather_candidates(self, context):
        return context['__parse']
