# ============================================================================
# FILE: change.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'change'
        self.kind = 'file'

    def on_init(self, context):
        changes = []
        for change in self.vim.call('execute', 'changes').split('\n')[2:]:
            l = change.split()
            if len(l) < 4:
                continue

            [linenr, col, text] = [int(l[1]), int(l[2]) + 1, ' '.join(l[3:])]

            changes.append({
                'word': '%4d-%-3d  %s' % (linenr, col, text),
                'action__path': self.vim.call(
                    'fnamemodify', self.vim.call('bufname', '%'), ':p'),
                'action__line': linenr,
                'action__col': col,
            })
        context['__changes'] = reversed(changes)

    def gather_candidates(self, context):
        return list(context['__changes'])
