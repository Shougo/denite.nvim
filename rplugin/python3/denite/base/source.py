# ============================================================================
# FILE: source.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing
from abc import ABC, abstractmethod
import denite.util
from denite.util import Nvim, UserContext, Candidates

from denite.base.kind import Base as Kind


class Base(ABC):

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'base'
        self.syntax_name = ''
        self.kind = Kind(self.vim)
        self.default_action = 'default'
        self.max_candidates = 1000
        self.matchers = ['matcher/fuzzy']
        self.sorters = ['sorter/rank']
        self.converters = []
        self.context = {}
        self.vars = {}
        self.is_public_context = False
        self.is_volatile = False

    def highlight(self) -> None:
        pass

    def define_syntax(self) -> None:
        self.vim.command(
            'syntax region ' + self.syntax_name + ' start=// end=/$/ '
            'contains=deniteMatchedRange contained')

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

    @abstractmethod
    def gather_candidates(self, context: UserContext) -> Candidates:
        pass

    def debug(self, expr: str) -> None:
        denite.util.debug(self.vim, expr)

    def get_status(self, context: UserContext) -> str:
        return ':'.join([self.name] +
                        ([str(context['args'])] if context['args'] else []))
