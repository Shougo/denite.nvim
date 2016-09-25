# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         Luis Carlos Cruz Carballo <lcruzc at linkux-it.com>
# License: MIT license
# ============================================================================

import re

from .base import Base
from denite.util import globruntime


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'command'
        self.kind = 'command'
        self.commands = []

        self.__re_command = re.compile(r'^\|:.+\|')
        self.__re_tokens = re.compile(r'^\|:(.+)\|[\t\s]+:([^\t]+)[\t\s]+(.+)')

    def on_init(self, context):
        runtimepath = self.vim.eval('&runtimepath')
        self._helpfiles = globruntime(runtimepath, 'doc/index.txt')

    def gather_candidates(self, context):
        if self.commands:
            return self.commands

        if not self._helpfiles:
            return []

        for helpfile in self._helpfiles:
            with open(helpfile) as doc:
                for line in [x for x in doc.readlines()
                             if self.__re_command.match(x)]:
                    tokens = self.__re_tokens.match(line).groups()
                    command = "execute input(':{0} ')".format(tokens[0])
                    self.commands.append({
                        'kind': 'command',
                        'action__command': command,
                        'source__command': ':' + tokens[0],
                        'word': '{0} - {1} -- {2}'.format(
                            tokens[0],
                            tokens[1].replace('\t', ''),
                            tokens[2],
                        ),
                    })

        return self.commands
