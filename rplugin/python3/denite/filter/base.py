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
        self.description = ''
        self.vars = {}

    @abstractmethod
    def filter(self, context):
        pass

    def convert_pattern(self, input_str):
        return ''

    def debug(self, expr):
        denite.util.debug(self.vim, expr)
