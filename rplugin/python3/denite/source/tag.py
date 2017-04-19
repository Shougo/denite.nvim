# ============================================================================
# FILE: tag.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import parse_tagline
import re


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.vim = vim
        self.name = 'tag'
        self.kind = 'file'

    def gather_candidates(self, context):
        candidates = []
        for f in self.vim.call('tagfiles'):
            with open(f, 'r') as ins:
                for line in ins:
                    if re.match('!', line) or not line:
                        continue
                    info = parse_tagline(line.rstrip(), f)
                    candidates.append({
                        'word': '{name} [{type}]  {ref}'.format(**info),
                        'action__path': info['file'],
                        'action__pattern': info['pattern']
                    })

        return sorted(candidates, key=lambda value: value['word'])
