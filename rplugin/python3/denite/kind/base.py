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
        self.persist_actions = ['echo']
        self.redraw_actions = []

    def debug(self, expr):
        denite.util.debug(self.vim, expr)

    def action_echo(self, context):
        context['messages'].append(str(context['targets']))

    def action_yank(self, context):
        _yank(self.vim, "\n".join([
            x['word'] for x in context['targets']
        ]))

    def action_ex(self, context):
        _ex(self.vim, "\n".join([
            x['word'] for x in context['targets']
        ]))

    def action_replace(self, context):
        self.vim.command('normal! gv')
        self.action_append(context)

    def action_append(self, context):
        for target in context['targets']:
            _paste(self.vim,
                   target.get('action__text', target['word']), 'p', 'v')


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
