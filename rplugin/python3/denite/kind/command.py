# ============================================================================
# FILE: command.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Kind(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'command'

    def action_default(self, context):
        target = context['targets'][0]
        self.vim.call(target['action__command'])
