# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         Luis Carlos Cruz Carballo <lcruzc at linkux-it.com>
# License: MIT license
# ============================================================================

import re

from .base import Base
from denite.util import globruntime
from re import sub


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'command'
        self.kind = 'command'
        self.commands = []

        self.__re_command = re.compile(r'^\|:.+\|')
        self.__re_tokens = re.compile(
            r'^\|:(.+)\|[\t\s]+:([^\t]+)[\t\s]+(.+)')

    def on_init(self, context):
        runtimepath = self.vim.eval('&runtimepath')
        self._helpfiles = globruntime(runtimepath, 'doc/index.txt')

    def gather_candidates(self, context):
        context['is_interactive'] = True

        if ' ' not in context['input'] or not self.vim.call(
                'denite#helper#has_cmdline'):
            if not self.commands:
                self._cache_helpfile()
            return self.commands + [{
                'action__command': x,
                'source__command': "execute input(':{0} ')".format(x),
                'word': x,
            } for x in self.vim.call('getcompletion', '', 'command')]

        prefix = sub('\w*$', '', context['input'])

        return [{
            'action__command': prefix + x,
            'source__command': "execute input(':{0} ')".format(prefix + x),
            'word': prefix + x,
        } for x in self.vim.call(
            'getcompletion', context['input'], 'cmdline')]

    def _cache_helpfile(self):
        for helpfile in self._helpfiles:
            with open(helpfile) as doc:
                for line in [x for x in doc.readlines()
                             if self.__re_command.match(x)]:
                    tokens = self.__re_tokens.match(line).groups()
                    command = "execute input(':{0} ')".format(tokens[0])
                    self.commands.append({
                        'action__command': command,
                        'source__command': ':' + tokens[0],
                        'word': '{0:<20} -- {1}'.format(
                            tokens[0], tokens[2],
                        ),
                    })
