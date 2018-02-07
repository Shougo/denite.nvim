# ============================================================================
# FILE: help.py
# AUTHOR: Mike Hartington <mikehartington at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import globruntime


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.vim = vim
        self.name = 'help'
        self.kind = 'command'

    def gather_candidates(self, context):
        candidates = []
        extend = candidates.extend
        for f in globruntime(context['runtimepath'], 'doc/tags'):
            with open(f, 'r') as ins:
                extend(list(map(lambda canidate: {
                    'word': canidate.split("\t", 1)[0],
                    'action__command': 'silent h ' + canidate.split("\t", 1)[0]
                }, ins)))
        return candidates
