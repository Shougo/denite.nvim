# ============================================================================
# FILE: filter.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing
from abc import ABC, abstractmethod

import denite.util
from denite.util import Nvim, UserContext, Candidates


class Base(ABC):

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'base'
        self.description = ''
        self.vars: typing.Dict[str, typing.Any] = {}

    @abstractmethod
    def filter(self, context: UserContext) -> Candidates:
        pass

    def convert_pattern(self, input_str: str) -> str:
        return ''

    def debug(self, expr: str) -> None:
        denite.util.debug(self.vim, expr)

    def print_message(self, context: UserContext, expr: typing.Any) -> None:
        context['messages'].append(self.name + ': ' + str(expr))

    def error_message(self, context: UserContext, expr: typing.Any) -> None:
        prefix = self.name + ': '
        if isinstance(expr, list):
            for line in expr:
                denite.util.error(self.vim, prefix + line)
        else:
            denite.util.error(self.vim, prefix + str(expr))
        context['error_messages'].append(prefix + str(expr))
