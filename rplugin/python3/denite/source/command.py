# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         Luis Carlos Cruz Carballo <lcruzc at linkux-it.com>
# License: MIT license
# ============================================================================

import re

from .base import Base


re_command = re.compile(r'^\|:.+\|')
re_tokens = re.compile(r'^\|:(.+)\|[\t\s]+:([^\t]+)[\t\s]+(.+)')


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'command'
        self.kind = 'command'
        self.commands = []

    def on_init(self, context):
        self._helpfile = self.vim.eval(
            'expand(findfile("doc/index.txt", &runtimepath))'
        )

    def gather_candidates(self, context):
        if self.commands:
            return self.commands

        if not self._helpfile:
            return []

        lines = open(self._helpfile).readlines()
        lines = filter(lambda line: re_command.match(line), lines)

        for line in lines:
            tokens = re_tokens.match(line).groups()
            self.commands.append({
                'kind': 'command',
                'action__command': tokens[0],
                'source__command': ':' + tokens[0],
                'word': '{0} - {1} -- {2}'.format(
                    tokens[0],
                    tokens[1].replace('\t', ''),
                    tokens[2],
                ),
            })

        return self.commands
