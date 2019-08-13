# ============================================================================
# FILE: command_history.py
# AUTHOR: pocari <caffelattenonsugar at gmail.com>
# License: MIT license
# ============================================================================

import re
import typing

from denite import util
from denite.base.source import Base
from denite.kind.command import Kind as Command
from denite.util import Nvim, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'command_history'
        self.kind = Kind(vim)
        self.vars = {
            'ignore_command_regexp': []
        }
        if self.vim.call('has', 'nvim'):
            self.vim.exec_lua(
                """
                local function getHistory()
                    local histories = {}
                    local number = vim.api.nvim_call_function('histnr', {':'})
                    for i=1, number do
                        histories[i] = {tostring(i),
                        vim.api.nvim_call_function('histget', {':', i})}
                    end
                    return histories
                end
                history_source = {get=getHistory}
                """)

    def gather_candidates(self, context: UserContext) -> Candidates:
        histories = self._get_histories()
        if not histories:
            return []

        max_len = len(histories[0][0])
        return [self._convert(r, max_len) for r in histories
                if len(r) > 1 and r[1]]

    def _get_histories(self) -> typing.List[str]:
        if self.vim.call('has', 'nvim'):
            histories = self.vim.lua.history_source.get()
            histories.reverse()
        else:
            histories = [
                [str(x), self.vim.call('histget', ':', x)]
                for x in reversed(range(1, self.vim.call('histnr', ':')+1))
            ]
        histories = self._remove_duplicate_entry(histories)
        if self.vars['ignore_command_regexp']:
            histories = list(filter(
                lambda history: not self._is_ignore_command(history[1]),
                histories
            ))
        return histories  # type: ignore

    def _remove_duplicate_entry(self,
                                seq: typing.List[str]) -> typing.List[str]:
        seen: typing.Set[str] = set()
        seen_add = seen.add
        return [
            x for x in seq
            if x[1].strip() not in seen and not seen_add(x[1].strip())
        ]

    def _filter_candidates(self,
                           histories: typing.List[str]) -> typing.List[str]:
        return [
            history for history in histories
            if not self._is_ignore_command(history[1])
        ]

    def _is_ignore_command(self, command: str) -> bool:
        for reg in self.vars['ignore_command_regexp']:
            if re.search(reg, command):
                return True
        return False

    def _convert(self, history: str, size: int) -> typing.Dict[
            str, typing.Any]:
        return {
            'word': ':' + history[1],
            'action__command': history[1],
            'source__index': int(history[0]),
            'action__histadd': True,
        }


class Kind(Command):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'command/history'
        self.redraw_actions = 'delete'
        self.persist_actions = 'delete'

    def action_edit(self, context: UserContext) -> None:
        target = context['targets'][0]
        command = util.input(self.vim, context,
                             "command > ",
                             target['action__command'],
                             'command')
        self._execute(context, command, target['action__histadd'])

    def action_delete(self, context: UserContext) -> None:
        for target in sorted(context['targets'],
                             key=lambda x: x['source__index'],
                             reverse=True):
            self.vim.call('histdel', ':', target['source__index'])
