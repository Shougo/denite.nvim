# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         Luis Carlos Cruz Carballo <lcruzc at linkux-it.com>
# License: MIT license
# ============================================================================

import re

from denite.base.source import Base
from denite.util import globruntime, Nvim, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'command'
        self.kind = 'command'
        self.commands: Candidates = []

        self._re_command = re.compile(r'^\|:.+\|')
        self._re_tokens = re.compile(
            r'^\|:(.+)\|[\t\s]+:([^\t]+)[\t\s]+(.+)')

    def on_init(self, context: UserContext) -> None:
        runtimepath = self.vim.eval('&runtimepath')
        self._helpfiles = globruntime(runtimepath, 'doc/index.txt')
        self._commands = globruntime(runtimepath, 'doc/index.txt')

    def gather_candidates(self, context: UserContext) -> Candidates:
        context['is_interactive'] = True

        has_cmdline = self.vim.call('denite#helper#has_cmdline')
        if ' ' not in context['input'] or not has_cmdline:
            if not self.commands:
                self._init_commands()
            return self.commands + [{
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

    def _init_commands(self) -> None:
        for helpfile in self._helpfiles:
            with open(helpfile) as doc:
                for line in [x for x in doc.readlines()
                             if self._re_command.match(x)]:
                    m = self._re_tokens.match(line)
                    if not m:
                        continue
                    tokens = m.groups()
                    command = f"execute input(':{tokens[0]} ')"
                    self.commands.append({
                        'action__command': command,
                        'word': '{0:<20} -- {1}'.format(
                            tokens[0], tokens[2],
                        ),
                    })
