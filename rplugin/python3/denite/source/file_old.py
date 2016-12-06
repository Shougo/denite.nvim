# ============================================================================
# FILE: file_old.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from os import path


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file_old'
        self.kind = 'file'

    def on_init(self, context):
        self.vim.command('wviminfo | rviminfo!')

    def gather_candidates(self, context):
        return [{'word': x, 'action__path': x}
                for x in self.vim.eval('v:oldfiles')
                if path.isfile(x) or self.vim.call('buflisted', x)]
