# ============================================================================
# FILE: jump.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'jump'
        self.kind = 'file'

    def on_init(self, context):
        jumps = []
        for jump in self.vim.call('execute', 'jumps').split('\n')[2:]:
            l = jump.split()
            if len(l) < 4:
                continue

            [linenr, col, file_text] = [int(l[1]), int(l[2]) + 1,
                                        ' '.join(l[3:])]

            lines = self.vim.call('getbufline', file_text, linenr)

            if lines:
                # text
                text = lines[0]
                path = file_text
            elif self.vim.call('getline', linenr) == file_text:
                # file loaded
                text = file_text
                path = self.vim.call('bufname', '%')
            elif self.vim.call('filereadable', file_text):
                # file not loaded
                text = file_text
                path = file_text
            else:
                continue

            jumps.append({
                'word': '%4d-%-3d  %s' % (linenr, col, text),
                'action__path': self.vim.call('fnamemodify', path, ':p'),
                'action__line': linenr,
                'action__col': col,
            })
        context['__jumps'] = reversed(jumps)

    def gather_candidates(self, context):
        return list(context['__jumps'])
