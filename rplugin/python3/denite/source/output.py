# ============================================================================
# FILE: output.py
# License: MIT license
# ============================================================================

import shlex
import subprocess

from .base import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'output'
        # why doesn't this seem to be working?
        self.default_action = 'yank'

    def gather_candidates(self, context):
        args = context['args']

        if not args:
            return []

        first = args[0]
        output = []
        if first[0] != '!':
            cmdline = ' '.join(args)
            output = self.vim.call('execute', cmdline).splitlines()[1:]
        else:
            cmdline = ' '.join([first[1:]] + args[1:])
            try:
                output = [x.decode(context['encoding']) for x in
                          subprocess.check_output(shlex.split(cmdline))
                          .splitlines()]
            except subprocess.CalledProcessError:
                return []
        return [{'word': x} for x in output]
