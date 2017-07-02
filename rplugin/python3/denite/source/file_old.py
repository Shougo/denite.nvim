# ============================================================================
# FILE: file_old.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from os import path
from ..kind.file import Kind as File
from denite.util import expand


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file_old'
        self.kind = Kind(vim)

    def on_init(self, context):
        # rviminfo! is broken in Vim8
        if self.vim.call('has', 'nvim'):
            self.vim.command('wviminfo | rviminfo!')

    def gather_candidates(self, context):
        return [{'word': x, 'action__path': x}
                for x in [expand(x) for x in self.vim.eval('v:oldfiles')]
                if path.isfile(x) or self.vim.call('buflisted', x)]


class Kind(File):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file'
        self.persist_actions += ['delete']
        self.redraw_actions += ['delete']

    def action_delete(self, context):
        delete_files = [x['action__path'] for x in context['targets']]
        self.vim.call('denite#helper#_set_oldfiles',
                      [x for x in self.vim.vvars['oldfiles']
                       if x not in delete_files])
