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
        self.kind = 'base'
        self.matchers = ['matcher_fuzzy']
        self.sorters = ['sorter_rank']
        self.converters = []
        self.context = {}
        self.vars = {}

    def highlight_syntax(self):
        pass

    @property
    def need_highlight(self):
        return self.__class__.highlight_syntax is not Base.highlight_syntax

    @abstractmethod
    def gather_candidate(self, context):
        pass

    def debug(self, expr):
        denite.util.debug(self.vim, expr)
