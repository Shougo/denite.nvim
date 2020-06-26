# ============================================================================
# FILE: base/source/interactive.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from denite.base.source import Base
from denite.util import Nvim, UserContext, expand, split_input


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.vars = {
            'grep_command': ['grep'],
            'grep_default_opts': ['-inH'],
            'grep_pattern_opt': ['-e'],
            'grep_separator': ['--'],
            'grep_final_opts': [],
        }

    def init_grep_args(self, context: UserContext) -> typing.List[str]:
        patterns = ['.*'.join(split_input(context['input']))]

        # Backwards compatibility for `ack`
        if (self.vars['grep_command'] and
                self.vars['grep_command'][0] == 'ack' and
                self.vars['grep_pattern_opt'] == ['-e']):
            self.vars['grep_pattern_opt'] = ['--match']

        args = [expand(self.vars['grep_command'][0])]
        args += self.vars['grep_command'][1:]
        args += self.vars['grep_default_opts']
        if self.vars['grep_pattern_opt']:
            for pattern in patterns:
                args += self.vars['grep_pattern_opt'] + [pattern]
            args += self.vars['grep_separator']
        else:
            args += self.vars['grep_separator']
            args += patterns
        args.append(context['__path'])
        args += self.vars['grep_final_opts']
        return args
