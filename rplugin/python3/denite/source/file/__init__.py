# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from ..base import Base
import glob
import os
from denite.util import abspath, expand


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file'
        self.kind = 'file'
        self.matchers = ['matcher/fuzzy', 'matcher/hide_hidden_files']

    def gather_candidates(self, context):
        context['is_interactive'] = True
        candidates = []
        path = (context['args'][1] if len(context['args']) > 1
                else context['path'])
        inp = expand(context['input'])
        filename = (inp if os.path.isabs(inp) else os.path.join(path, inp))
        if context['args'] and context['args'][0] == 'new':
            candidates.append({
                'word': filename,
                'abbr': '[new] ' + filename,
                'action__path': abspath(self.vim, filename),
            })
        else:
            glb = os.path.dirname(filename) if os.path.dirname(
                filename) != '/' else ''
            glb += '/.*' if os.path.basename(
                filename).startswith('.') else '/*'
            for f in glob.glob(glb):
                candidates.append({
                    'word': f,
                    'abbr': f + ('/' if os.path.isdir(f) else ''),
                    'kind': ('directory' if os.path.isdir(f) else 'file'),
                    'action__path': abspath(self.vim, f),
                })
        return candidates
