# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.kind import Base
from denite import util


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'command'
        self.default_action = 'execute'

    def action_execute(self, context):
        target = context['targets'][0]
        self._execute(context,
                      target['action__command'],
                      target.get('action__is_pause', False))

    def action_edit(self, context):
        target = context['targets'][0]
        command = util.input(self.vim, context,
                             "command > ",
                             target['action__command'],
                             'command')
        self._execute(context, command,
                      target.get('action__is_pause', False))

    def _execute(self, context, command, is_pause):
        if not command:
            return
        if context['firstline'] != context['lastline']:
            command = '{},{}{}'.format(
                context['firstline'], context['lastline'], command)
        self.vim.call(
            'denite#util#execute_command', command, is_pause)
