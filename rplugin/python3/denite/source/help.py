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
        help_docs = {}
        for f in globruntime(context['runtimepath'], 'doc/tags'):
            with open(f, 'r') as ins:
                for line in ins:
                    name = line.split("\t", 1)[0]
                    help_docs[name] = {
                        'word': name,
                        'action__command': 'silent help ' + name
                    }

        return sorted(help_docs.values(), key=lambda value: value['word'])
