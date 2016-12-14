# ============================================================================
# FILE: base.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import denite.util


class Base(object):

    def __init__(self, vim):
        self.vim = vim
        self.name = 'base'
        self.persist_actions = []

    def debug(self, expr):
        denite.util.debug(self.vim, expr)

    def action_yank(self, context):
        self.__yank(self.vim, "\n".join(
            [x['word'] for x in context['targets']]))

    def __yank(self, vim, word):
        vim.call('setreg', '"', word, 'v')
        if vim.call('has', 'clipboard'):
            vim.call('setreg', vim.eval('v:register'), word, 'v')
