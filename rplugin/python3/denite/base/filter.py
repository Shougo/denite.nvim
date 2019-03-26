# ============================================================================
# FILE: filter.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from abc import ABC, abstractmethod
import denite.util


class Base(ABC):

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

    def print_message(self, context, expr):
        context['messages'].append(self.name + ': ' + str(expr))

    def error_message(self, context, expr):
        prefix = self.name + ': '
        if isinstance(expr, list):
            for line in expr:
                denite.util.error(self.vim, prefix + line)
        else:
            denite.util.error(self.vim, prefix + str(expr))
        context['error_messages'].append(prefix + str(expr))
