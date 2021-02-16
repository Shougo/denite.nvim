# ============================================================================
# FILE: help.py
# AUTHOR: Mike Hartington <mikehartington at gmail.com>
# License: MIT license
# ============================================================================

from pynvim import Nvim
import re

from denite.base.source import Base
from denite.kind.command import Kind as Command

from denite.util import globruntime, clearmatch, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.vim = vim
        self.name = 'help'
        self.kind = Kind(vim)

    def gather_candidates(self, context: UserContext) -> Candidates:
        candidates: Candidates = []
        extend = candidates.extend
        for f in globruntime(context['runtimepath'], 'doc/tags'):
            with open(f, 'r') as ins:
                root = re.sub('tags$', '', f)
                extend(list(map(lambda candidate: {
                    'word': candidate.split("\t", 1)[0],
                    'action__command': (
                        'silent h ' + candidate.split("\t", 1)[0]
                    ),
                    '__path': root + candidate.split("\t")[1],
                    '__tag': candidate.split("\t")[2].rstrip('\n')[1:],
                }, ins)))
        return candidates


class Kind(Command):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.vim = vim
        self.name = 'help'

    def action_preview(self, context: UserContext) -> None:
        target = context['targets'][0]

        if (context['auto_action'] != 'preview' and
                self._get_preview_window() and
                self._previewed_target == target):
            self.vim.command('pclose!')
            return

        path = target['__path']
        listed = self.vim.call('buflisted', path)
        prev_id = self.vim.call('win_getid')

        self.vim.call('denite#helper#preview_file', context, path)
        self.vim.command('wincmd P')
        self.vim.current.window.options['foldenable'] = False

        if not listed:
            self._add_previewed_buffer(self.vim.call('bufnr', '%'))

        # jump to help tag
        pattern = r'\V' + target['__tag']
        self.vim.command('normal! gg')
        self.vim.call('search', pattern)
        self.vim.command('normal! zt')
        self._highlight(context, pattern)

        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target

    def _get_preview_window(self) -> bool:
        return bool(self.vim.call('denite#helper#_get_preview_window'))

    def _add_previewed_buffer(self, bufnr: int) -> None:
        previewed_buffers = self.vim.vars['denite#_previewed_buffers']
        previewed_buffers[str(bufnr)] = 1
        self.vim.vars['denite#_previewed_buffers'] = previewed_buffers

    def _highlight(self, context: UserContext, pattern: int) -> None:
        clearmatch(self.vim)
        self.vim.current.window.vars['denite_match_id'] = self.vim.call(
            'matchadd', context['highlight_preview_line'], pattern)
