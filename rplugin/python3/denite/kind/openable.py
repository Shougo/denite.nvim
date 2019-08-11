# ============================================================================
# FILE: openable.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from abc import abstractmethod
from copy import copy

from denite.base.kind import Base
from denite.util import Nvim, UserContext, Candidate

Fallback = typing.Callable[[UserContext], None]


class Kind(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'openable'
        self.default_action = 'open'

    @abstractmethod
    def action_open(self, context: UserContext) -> None:
        pass

    @abstractmethod
    def _winid(self, target: Candidate) -> typing.Optional[int]:
        pass

    def action_split(self, context: UserContext) -> None:
        if self._is_current_buffer_empty():
            self.action_open(context)
            return

        for target in context['targets']:
            new_context = copy(context)
            new_context['targets'] = [target]

            self.vim.command('split')
            self.action_open(new_context)

    def action_vsplit(self, context: UserContext) -> None:
        if self._is_current_buffer_empty():
            self.action_open(context)
            return

        for target in context['targets']:
            new_context = copy(context)
            new_context['targets'] = [target]

            self.vim.command('vsplit')
            self.action_open(new_context)

    def action_tabopen(self, context: UserContext) -> None:
        if self._is_current_buffer_empty():
            self.action_open(context)
            return

        hidden = self.vim.options['hidden']
        try:
            self.vim.options['hidden'] = False
            for target in context['targets']:
                new_context = copy(context)
                new_context['targets'] = [target]

                self.vim.command('tabnew')
                self.action_open(new_context)
        finally:
            self.vim.options['hidden'] = hidden

    def action_switch(self, context: UserContext) -> None:
        self._action_switch(context, self.action_open)

    def action_tabswitch(self, context: UserContext) -> None:
        self._action_switch(context, self.action_tabopen)

    def action_splitswitch(self, context: UserContext) -> None:
        self._action_switch(context, self.action_split)

    def action_vsplitswitch(self, context: UserContext) -> None:
        self._action_switch(context, self.action_vsplit)

    def _action_switch(self, context: UserContext,
                       fallback: Fallback) -> None:
        for target in context['targets']:
            winid = self._winid(target)
            if winid:
                self.vim.call('win_gotoid', winid)
                if callable(self._jump):
                    self._jump(context, target)
            else:
                fallback(context)

    def _jump(self, context: UserContext, target: Candidate) -> None:
        if 'action__pattern' in target:
            self.vim.call('search', target['action__pattern'], 'w')

        line = int(target.get('action__line', 0))
        col = int(target.get('action__col', 0))

        try:
            if line > 0:
                self.vim.call('cursor', [line, 0])
                if 'action__col' not in target:
                    pos = self.vim.current.line.lower().find(
                        context['input'].lower())
                    if pos >= 0:
                        self.vim.call('cursor', [0, pos + 1])
            if col > 0:
                self.vim.call('cursor', [0, col])
        except Exception:
            pass

        # Open folds
        self.vim.command('normal! zv')

    def _is_current_buffer_empty(self) -> bool:
        buffer = self.vim.current.buffer
        return buffer.name == '' and len(buffer) == 1 and buffer[0] == ''
