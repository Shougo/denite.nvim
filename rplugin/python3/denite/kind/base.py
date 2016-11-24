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

    def debug(self, expr):
        denite.util.debug(self.vim, expr)

    def action_yank(self, context):
        target = context['targets'][0]
        self.__yank(self.vim, target['word'])

    def __yank(self, vim, word):
        vim.call('setreg', '"', word, 'v')
        if vim.eval('has("clipboard")') == 1:
            vim.call('setreg', vim.eval('v:register'), word, 'v')
