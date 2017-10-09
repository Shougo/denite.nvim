# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'command'
        self.default_action = 'execute'

    def action_execute(self, context):
        target = context['targets'][0]
        self.vim.call('denite#util#execute_command',
                      target['action__command'])

    def action_edit(self, context):
        target = context['targets'][0]
        command = self.vim.call('input', 'Command: ',
                                target['action__command'] + ' ', 'command')
        if command:
            self.vim.call('denite#util#execute_command',
                          target['action__command'])
