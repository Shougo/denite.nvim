# ============================================================================
# FILE: jump.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base

import re


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'jump'
        self.kind = 'file'

    def on_init(self, context):
        if self.vim.call('exists', '*getjumplist'):
            context['__jumps'] = self._get_jumplist(context)
        else:
            context['__jumps'] = self._parse(context)

    def _get_jumplist(self, context):
        buffers = self.vim.buffers
        [l, index] = self.vim.call('getjumplist')

        def get(l):
            return l[0] if l else ''

        return [{
            'word': '%s: %4d-%-3d %s' % (
                buffers[int(x['bufnr'])].name, x['lnum'], x['col'],
                get(self.vim.call('getbufline', x['bufnr'], x['lnum']))),
            'action__path': self.vim.call(
                'fnamemodify', buffers[int(x['bufnr'])].name, ':p'),
            'action__bufnr': x['bufnr'],
            'action__line': x['lnum'],
            'action__col': x['col'],
        } for x in l]

    def _parse(self, context):
        jumps = []
        for jump in self.vim.call('execute', 'jumps').split('\n'):
            texts = jump.split()
            if len(texts) < 4 or not re.search('^\d+$', texts[1]):
                continue

            [linenr, col, file_text] = [
                int(texts[1]), int(texts[2]) + 1, ' '.join(texts[3:])]

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
        return list(reversed(jumps))

    def gather_candidates(self, context):
        return context['__jumps']
