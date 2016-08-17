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
