# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
import glob
import os


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file'
        self.kind = 'file'

    def gather_candidates(self, context):
        context['is_interactive'] = True
        candidates = []
        for f in glob.glob(context['input'] + '*'):
            candidates.append({
                'word': f,
                'abbr': f + ('/' if os.path.isdir(f) else ''),
                'action__path': os.path.abspath(f),
            })
        return candidates
