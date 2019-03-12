# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         Luis Carlos Cruz Carballo <lcruzc at linkux-it.com>
# License: MIT license
# ============================================================================

import re

from denite.base.source import Base
from denite.util import globruntime


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'command'
        self.kind = 'command'
        self.commands = []

        self._re_command = re.compile(r'^\|:.+\|')
        self._re_tokens = re.compile(
            r'^\|:(.+)\|[\t\s]+:([^\t]+)[\t\s]+(.+)')

    def on_init(self, context):
        runtimepath = self.vim.eval('&runtimepath')
        self._helpfiles = globruntime(runtimepath, 'doc/index.txt')
        self._commands = globruntime(runtimepath, 'doc/index.txt')

    def gather_candidates(self, context):
        context['is_interactive'] = True

        has_cmdline = self.vim.call('denite#helper#has_cmdline')
        if ' ' not in context['input'] or not has_cmdline:
            if not self.commands:
                self._init_commands()
            return self.commands + [{
                'action__command': x,
                'action__is_pause': True,
                'word': x,
            } for x in self.vim.call('getcompletion', '', 'command')]

        prefix = re.sub(r'\w*$', '', context['input'])

        candidates = [{
            'action__command': prefix + x,
            'action__is_pause': True,
            'word': prefix + x,
        } for x in self.vim.call(
            'getcompletion', context['input'], 'cmdline')]
        if not candidates:
            candidates = [{
                'action__command': context['input'],
                'action__is_pause': True,
                'word': context['input'],
            }]
        return candidates

    def _init_commands(self):
        for helpfile in self._helpfiles:
            with open(helpfile) as doc:
                for line in [x for x in doc.readlines()
                             if self._re_command.match(x)]:
                    tokens = self._re_tokens.match(line).groups()
                    command = f"execute input(':{tokens[0]} ')"
                    self.commands.append({
                        'action__command': command,
                        'word': '{0:<20} -- {1}'.format(
                            tokens[0], tokens[2],
                        ),
                    })
