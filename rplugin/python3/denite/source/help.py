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
        for file in globruntime(context['runtimepath'], 'doc/*.txt'):
            helpDoc = path.splitext(path.basename(file))[0]
            helpDocs[helpDoc] = {
                'word': helpDoc,
                'action__command': 'help ' + helpDoc
            }

        return sorted(helpDocs.values(), key=lambda value: value['word'])
