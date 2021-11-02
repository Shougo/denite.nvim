# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         Luis Carlos Cruz Carballo <lcruzc at linkux-it.com>
# License: MIT license
# ============================================================================

from pynvim import Nvim
import re

from denite.base.source import Base
from denite.util import UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'command'
        self.kind = 'command'

    def gather_candidates(self, context: UserContext) -> Candidates:
        context['is_interactive'] = True

        has_cmdline = self.vim.call('denite#helper#has_cmdline')
        if not has_cmdline:
            return []
        if ' ' not in context['input'] or not has_cmdline:
            return [{
                'action__command': x,
                'word': x,
            } for x in self.vim.call('getcompletion', '', 'command')]

        prefix = re.sub(r'\w*$', '', context['input'])

        candidates = [{
            'action__command': prefix + x,
            'word': prefix + x,
            'action__histadd': True,
        } for x in self.vim.call(
            'getcompletion', context['input'], 'cmdline')]
        if not candidates:
            candidates = [{
                'action__command': context['input'],
                'word': context['input'],
                'action__histadd': True,
            }]
        return candidates
