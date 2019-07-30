# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.kind import Base
from denite import util
from denite.util import Nvim, UserContext


class Kind(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'command'
        self.default_action = 'execute'

    def action_execute(self, context: UserContext) -> None:
        target = context['targets'][0]
        self._execute(context, target['action__command'],
                      target.get('action__histadd', False))

    def action_edit(self, context: UserContext) -> None:
        target = context['targets'][0]
        command = util.input(self.vim, context,
                             "command > ",
                             target['action__command'],
                             'command')
        self._execute(context, command,
                      target.get('action__histadd', False))

    def _execute(self, context: UserContext,
                 command: str, histadd: bool) -> None:
        if not command:
            return
        if context['firstline'] != context['lastline']:
            command = '{},{}{}'.format(
                context['firstline'], context['lastline'], command)
        self.vim.call('denite#util#execute_command', command, False)
        if histadd:
            self.vim.call('histadd', ':', command)
