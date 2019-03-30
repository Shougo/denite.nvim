# ============================================================================
# FILE: kind.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import denite.util


class Base(object):

    def __init__(self, vim):
        self.vim = vim
        self.name = 'base'
        self.default_action = 'echo'
        self.persist_actions = ['echo', 'preview']
        self.redraw_actions = []

    def debug(self, expr):
        denite.util.debug(self.vim, expr)

    def action_echo(self, context):
        self.vim.command('redraw')
        for target in context['targets']:
            self.debug(target)
        self.vim.call('denite#util#getchar')

    def action_yank(self, context):
        _yank(self.vim, "\n".join([
            x['word'] for x in context['targets']
        ]))

    def action_ex(self, context):
        _ex(self.vim, "\n".join([
            x['word'] for x in context['targets']
        ]))

    def action_replace(self, context):
        self.vim.command('normal! viw')
        self.action_append(context)

    def action_append(self, context):
        for target in context['targets']:
            _paste(self.vim,
                   target.get('action__text', target['word']), 'p', 'v')

    def get_action_names(self):
        return ['default'] + [x.replace('action_', '') for x in dir(self)
                              if x.find('action_') == 0]

    def action_preview(self, context):
        pass


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)


def _yank(vim, word):
    vim.call('setreg', '"', word, 'v')
    if vim.call('has', 'clipboard'):
        vim.call('setreg', vim.eval('v:register'), word, 'v')


def _ex(vim, word):
    # NOTE:
    # <C-b> (\x02) in a command-line move the caret to the beginning.
    # Somehow the key above works in 'input()' function as well.
    expr = vim.call('input', ':', ' %s\x02' % word, 'command')
    if expr:
        vim.command(expr)


def _paste(vim, word, command, regtype):
    if regtype == '':
        regtype = 'v'

    # Paste.
    old_reg = [vim.call('getreg', '"'), vim.call('getregtype', '"')]

    vim.call('setreg', '"', word, regtype)
    try:
        vim.command('normal! ""' + command)
    finally:
        vim.call('setreg', '"', old_reg[0], old_reg[1])

    # Open folds
    vim.command('normal! zv')
