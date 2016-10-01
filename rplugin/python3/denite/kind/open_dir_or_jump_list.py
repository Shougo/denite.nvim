# ============================================================================
# FILE: open_or_jump_list.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         okamos <himinato.k at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from os import path


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'open_dir_or_jump_list'

    def action_default(self, context):
        target = context['targets'][0]
        action_path = target['action__path']

        is_dir = path.isdir(action_path)

        if is_dir:
            action_command = ('call denite#start('
                              "[{'name': 'buffer_dir', 'args': ['%s']}])"
                              % (action_path))
            self.vim.command(action_command)
        else:
            if self.vim.call('fnamemodify',
                             self.vim.current.buffer.name,
                             ':p') != action_path:
                self.vim.call(
                    'denite#util#execute_path', 'edit', action_path)
