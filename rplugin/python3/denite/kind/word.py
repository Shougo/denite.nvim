# ============================================================================
# FILE: word.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'word'
        self.default_action = 'append'

    def action_append(self, context):
        for target in context['targets']:
            paste(self.vim, target['action__text'], 'p', 'v')


def paste(vim, word, command, regtype):
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
