# ============================================================================
# FILE: jump_list.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Kind(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'jump_list'

    def action_default(self, context):
        target = context['targets'][0]
        self.vim.call('denite#util#execute_path', 'edit',
                      target['action__path'])
        if 'action__line' in target:
            self.vim.current.window.cursor = (target['action__line'], 0)
        if 'action__col' in target:
            self.vim.current.window.cursor = (0, target['action__col'])
        # Open folds
        self.vim.command('normal! zv')
