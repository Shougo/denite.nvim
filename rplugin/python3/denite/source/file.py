# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
import glob
import os
from denite.util import abspath


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file'
        self.kind = 'file'
        self.matchers = ['matcher_fuzzy', 'matcher_hide_hidden_files']

    def gather_candidates(self, context):
        context['is_interactive'] = True
        candidates = []
        path = (context['args'][1] if len(context['args']) > 1
                else context['path'])
        filename = (context['input']
                    if os.path.isabs(context['input'])
                    else os.path.join(path, context['input']))
        if context['args'] and context['args'][0] == 'new':
            candidates.append({
                'word': filename,
                'abbr': '[new] ' + filename,
                'action__path': abspath(self.vim, filename),
            })
        else:
            for f in glob.glob(os.path.dirname(filename) + '/*'):
                candidates.append({
                    'word': f,
                    'abbr': f + ('/' if os.path.isdir(f) else ''),
                    'kind': ('directory' if os.path.isdir(f) else 'file'),
                    'action__path': abspath(self.vim, f),
                })
        return candidates
