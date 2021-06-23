# ============================================================================
# FILE: file/old.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pynvim import Nvim

from denite.kind.file import Kind as File
from denite.base.source import Base
from denite.util import expand, safe_call, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file/old'
        self.kind = Kind(vim)

    def on_init(self, context: UserContext) -> None:
        # Note: rviminfo! is broken in Vim8 before 8.2.2494
        if self.vim.call('has', 'nvim') or self.vim.call(
                'has', 'patch-8.2.2494'):
            self.vim.command('wviminfo | rviminfo!')

    def gather_candidates(self, context: UserContext) -> Candidates:
        oldfiles = [
            expand(x) for x in self.vim.call('denite#helper#_get_oldfiles')
            if not self.vim.call('bufexists', x) or
            safe_call(lambda: self.vim.call('getbufvar', x, '&buftype'),
                      '') == '']
        return [{'word': x, 'action__path': x} for x in oldfiles]


class Kind(File):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file'
        self.persist_actions += ['delete']
        self.redraw_actions += ['delete']

    def action_delete(self, context: UserContext) -> None:
        delete_files = [x['action__path'] for x in context['targets']]
        self.vim.call('denite#helper#_set_oldfiles',
                      [x for x in self.vim.vvars['oldfiles']
                       if x not in delete_files])
