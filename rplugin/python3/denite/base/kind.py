# ============================================================================
# FILE: base/kind.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pynvim import Nvim
import typing

import denite.util
from denite.util import UserContext, Candidate


class Base(object):

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'base'
        self.default_action = 'echo'
        self.persist_actions: typing.List[str] = [
            'echo', 'preview', 'preview_bat'
        ]
        self.redraw_actions: typing.List[str] = []
        self._previewed_target: typing.Dict[str, Candidate] = {}
        self._previewed_winid: int = 0

    def debug(self, expr: str) -> None:
        denite.util.debug(self.vim, expr)

    def action_echo(self, context: UserContext) -> None:
        self.vim.command('redraw')
        for target in context['targets']:
            self.debug(target)
        self.vim.call('denite#util#getchar')

    def action_yank(self, context: UserContext) -> None:
        _yank(self.vim, "\n".join([
            x['word'] for x in context['targets']
        ]))

    def action_ex(self, context: UserContext) -> None:
        _ex(self.vim, "\n".join([
            x['word'] for x in context['targets']
        ]))

    def action_replace(self, context: UserContext) -> None:
        self.vim.command('normal! viw')
        self.action_append(context)

    def action_append(self, context: UserContext) -> None:
        for target in context['targets']:
            _paste(self.vim,
                   target.get('action__text', target['word']), 'p',
                   target.get('action__regtype', 'v'))

    def action_insert(self, context: UserContext) -> None:
        for target in context['targets']:
            _paste(self.vim,
                   target.get('action__text', target['word']), 'P',
                   target.get('action__regtype', 'v'))

    def get_action_names(self) -> typing.List[str]:
        return ['default'] + [x.replace('action_', '') for x in dir(self)
                              if x.find('action_') == 0]

    def action_preview(self, context: UserContext) -> None:
        pass

    def action_preview_bat(self, context: UserContext) -> None:
        pass

    def action_defx(self, context: UserContext) -> None:
        if not self.vim.call('exists', '*defx#start_candidates'):
            return

        self.vim.call('defx#start_candidates',
                      [x.get('action__path', x['word']) for x
                       in context['targets']], {})

    def preview_terminal(self, context: UserContext, cmd: typing.List[str],
                         action_name: str) -> None:
        target = context['targets'][0]

        if (self._previewed_target == target and
                context['auto_action'] == action_name):
            # Skip if auto_action
            return

        prev_id = self.vim.call('win_getid')
        is_nvim = self.vim.call('has', 'nvim')

        if self._previewed_winid:
            self.vim.call('win_gotoid', self._previewed_winid)
            if self.vim.call('win_getid') != prev_id:
                self.vim.command('bdelete! ' +
                                 str(self.vim.call('bufnr', '%')))
                self.vim.vars['denite#_previewing_bufnr'] = -1
            self.vim.call('win_gotoid', prev_id)
            self._previewed_winid = 0

            if self._previewed_target == target:
                # Close the window only
                return

        self.vim.call('denite#helper#preview_file', context, '')

        if is_nvim:
            self.vim.call('termopen', cmd)
        else:
            self.vim.call('term_start', cmd, {
                'curwin': True,
                'term_kill': 'kill',
            })

        bufnr = self.vim.call('bufnr', '%')
        self._previewed_winid = self.vim.call('win_getid')
        self.vim.vars['denite#_previewing_bufnr'] = bufnr

        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target


class Kind(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)


def _yank(vim: Nvim, word: str) -> None:
    vim.call('setreg', '"', word, 'v')
    if vim.call('has', 'clipboard'):
        vim.call('setreg', vim.eval('v:register'), word, 'v')


def _ex(vim: Nvim, word: str) -> None:
    # NOTE:
    # <C-b> (\x02) in a command-line move the caret to the beginning.
    # Somehow the key above works in 'input()' function as well.
    expr = vim.call('input', ':', ' %s\x02' % word, 'command')
    if expr:
        vim.command(expr)


def _paste(vim: Nvim, word: str, command: str, regtype: str) -> None:
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
