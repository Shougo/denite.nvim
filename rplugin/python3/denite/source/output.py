# ============================================================================
# FILE: output.py
# License: MIT license
# ============================================================================

import re

from .base import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'output'
        # why doesn't this seem to be working?
        self.default_action = 'yank'

    def define_syntax(self):
        cmd = self.context['args'][0]
        if re.fullmatch(r'hi(ghlight)?(!)?', cmd):
            self.define_syntax_for_highlight(cmd)

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
            output = self.vim.call('system', cmdline).splitlines()
        return [{'word': x} for x in output]

    def define_syntax_for_highlight(self, cmd):
        self.vim.command('syntax include syntax/vim.vim')
        hi_list = self.vim.call('execute', cmd).splitlines()[1:]
        for hi in (h.split()[0] for h in hi_list):
            syn_hi_name = (
                'syntax match vimHiGroup' +
                ' /' + hi + r'\>/' +
                ' nextgroup=' + hi +
                ' skipwhite'
            )
            syn_hi_xxx = (
                'syntax match ' + hi +
                ' /xxx/' +
                ' contained' +
                ' nextgroup=@vimHighlightCluster' +
                ' skipwhite'
            )
            self.vim.command(syn_hi_name)
            self.vim.command(syn_hi_xxx)
