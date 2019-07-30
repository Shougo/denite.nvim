# ============================================================================
# FILE: filetype.py
# AUTHOR: Prabir Shrestha <mail at prabir.me>
# License: MIT license
# ============================================================================

from os import path

from denite.base.source import Base
from denite.util import globruntime, Nvim, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'filetype'
        self.kind = 'command'

    def gather_candidates(self, context: UserContext) -> Candidates:
        filetypes = {}

        for file in globruntime(context['runtimepath'], 'syntax/*.vim'):
            filetype = path.splitext(path.basename(file))[0]
            filetypes[filetype] = {
                'word': filetype,
                'action__command': 'set filetype=' + filetype
            }

        return sorted(filetypes.values(), key=lambda value: value['word'])
