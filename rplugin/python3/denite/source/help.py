# ============================================================================
# FILE: help.py
# AUTHOR: Mike Hartington <mikehartington at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from os import path
from denite.util import globruntime


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.vim = vim
        self.name = 'help'
        self.kind = 'command'

    def gather_candidates(self, context):
        helpDocs = {}
        for file in globruntime(context['runtimepath'], 'doc/tags'):
            with open(file, 'r') as ins:
                for line in ins:
                    name = line.split("\t", 1)[0]
                    helpDocs[name] = {
                        'word': name,
                        'action__command': 'help ' + name
                    }

        return sorted(helpDocs.values(), key=lambda value: value['word'])
