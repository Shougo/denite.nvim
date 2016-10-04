# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file'

    def action_default(self, context):
        target = context['targets'][0]
        path = target['action__path']
        if self.vim.call('fnamemodify',
                         self.vim.current.buffer.name, ':p') != path:
            self.vim.call(
                'denite#util#execute_path', 'edit', path)
        line = int(target.get('action__line', 0))
        col = int(target.get('action__col', 0))
        try:
            if line > 0:
                self.vim.call('cursor', [line, 0])
            if col > 0:
                self.vim.call('cursor', [0, col])
        except Exception:
            pass

        # Open folds
        self.vim.command('normal! zv')
