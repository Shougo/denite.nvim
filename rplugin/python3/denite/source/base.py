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
        self.syntax_name = ''
        self.kind = 'base'
        self.default_action = 'default'
        self.max_candidates = 1000
        self.matchers = ['matcher_fuzzy']
        self.sorters = ['sorter_rank']
        self.converters = []
        self.context = {}
        self.vars = {}
        self.is_public_context = False

    def highlight(self):
        pass

    def define_syntax(self):
        self.vim.command(
            'syntax region ' + self.syntax_name + ' start=// end=/$/ '
            'contains=deniteMatchedRange contained')

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

    @abstractmethod
    def gather_candidate(self, context):
        pass

    def debug(self, expr):
        denite.util.debug(self.vim, expr)

    def get_status(self, context):
        return ':'.join([self.name] + context['args'])
