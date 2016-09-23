# ============================================================================
# FILE: filetype.py
# AUTHOR: Prabir Shrestha <mail at prabir.me>
# License: MIT license
# ============================================================================

from .base import Base
from os import path, listdir


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'filetype'
        self.kind = 'command'

    def gather_candidates(self, context):
        # since self.vim.list_runtime_paths() does not work in vim 8
        # use eval instead
        rtps = self.vim.eval('&runtimepath').split(',')
        filetypes = {}

        for rtp in rtps:
            syntax_dir = path.join(rtp, 'syntax')
            if path.exists(syntax_dir):
                for file in listdir(syntax_dir):
                    if file.endswith('.vim'):
                        filetype = path.splitext(file)[0]
                        filetypes[filetype] = {
                            'word': filetype,
                            'action__command': 'set filetype=' + filetype
                        }

        return sorted(filetypes.values(), key=lambda value: value['word'])
