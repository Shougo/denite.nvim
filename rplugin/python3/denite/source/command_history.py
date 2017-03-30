# -*- coding: utf-8 -*-
# FILE: command_history.py
# AUTHOR: pocari <caffelattenonsugar at gmail.com>
# License: MIT license
import re

from denite import util
from .base import Base
from ..kind.command import Kind as Command


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'command_history'
        self.kind = Kind(vim)
        self.vars = {
            'ignore_command_regexp': []
        }

    def gather_candidates(self, context):
        histories = self._get_histories()
        if not histories:
            return []

        max_len = len(histories[0][0])
        return [self._convert(r, max_len) for r in histories if len(r) > 1]

    def _get_histories(self):
        histories = [
            [str(x), self.vim.call('histget', ':', x)]
            for x in reversed(range(1, self.vim.call('histnr', ':')))
        ]
        histories = self._remove_duplicate_entry(histories)
        if self.vars['ignore_command_regexp']:
            histories = list(filter(
                lambda history: not self._is_ignore_command(history[1]),
                histories
            ))
        return histories

    def _remove_duplicate_entry(self, seq):
        seen = set()
        seen_add = seen.add
        return [
            x for x in seq
            if x[1].strip() not in seen and not seen_add(x[1].strip())
        ]

    def _filter_candidates(self, histories):
        return [
            history for history in histories
            if not self._is_ignore_command(history[1])
        ]

    def _is_ignore_command(self, command):
        for reg in self.vars['ignore_command_regexp']:
            if re.search(reg, command):
                return True
        return False

    def _convert(self, history, size):
        return {
            'word': '%*s %s' % (size, history[0], history[1]),
            'action__command': history[1]
        }


class Kind(Command):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'command/history'

    def action_edit_and_execute(self, context):
        target = context['targets'][0]
        edited = util.input(self.vim, context,
                            "command > ",
                            target['action__command'],
                            'command')
        if edited:
            self.vim.call('denite#util#execute_command', edited)
