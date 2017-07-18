# ============================================================================
# FILE: output.py
# License: MIT license
# ============================================================================

from .base import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'output'
        # why doesn't this seem to be working?
        self.default_action = 'yank'

    def gather_candidates(self, context):
        output = []
        args = context['args']

        if not args:
            return output

        first = args[0]
        if first[0] != '!':
            output += self.vim.call('execute', ' '.join(args)).splitlines()[1:]
        else:
            output += (self.vim.call('system',
                                     ' '.join([first[1:]] + args[1:])
                                     ).splitlines())

        return [{'word': x}
                for x in output]
