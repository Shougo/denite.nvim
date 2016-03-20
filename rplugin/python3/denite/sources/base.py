# ============================================================================
# FILE: base.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from abc import abstractmethod
import denite.util


class Base(object):

    def __init__(self, vim):
        self.vim = vim
        self.name = 'base'
        self.matchers = []
        self.sorters = []
        self.converters = []
        self.rank = 100

    @abstractmethod
    def gather_candidate(self, context):
        pass

    def debug(self, expr):
        denite.util.debug(self.vim, expr)
