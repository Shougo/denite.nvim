# ============================================================================
# FILE: help.py
# AUTHOR: Mike Hartington <mikehartington at gmail.com>
# License: MIT license
# ============================================================================

from os import sep
from pathlib import Path
from pynvim import Nvim

from denite.base.source import Base
from denite.util import globruntime, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.vim = vim
        self.name = 'help'
        self.kind = 'file'

    def gather_candidates(self, context: UserContext) -> Candidates:
        candidates: Candidates = []
        extend = candidates.extend
        for f in globruntime(context['runtimepath'], 'doc/tags'):
            with open(f, 'r') as ins:
                root = str(Path(f).parent)
                extend(list(map(lambda candidate: {
                    'word': candidate.split("\t", 1)[0],
                    'action__path': (
                        root + sep + candidate.split("\t")[1]
                    ),
                    'action__pattern': (
                        r'\V' + candidate.split("\t")[2].rstrip('\n')[1:]
                    ),
                }, ins)))
        return candidates
