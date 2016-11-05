# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
import re


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file'
        self.default_action = 'open'

    def action_open(self, context):
        target = context['targets'][0]
        path = target['action__path']

        if re.match('^\w+://', path):
            # URI
            self.vim.call('denite#util#open', path)
            return

        if self.vim.call('bufwinnr', path) <= 0:
            self.vim.call(
                'denite#util#execute_path', 'edit', path)
        elif self.vim.call('bufwinnr', path) != self.vim.current.buffer:
            self.vim.call(
                'denite#util#execute_path', 'buffer', path)
        self.__jump(context, target)

    def action_preview(self, context):
        target = context['targets'][0]
        path = target['action__path']

        preview_window = self.get_preview_window()
        if (preview_window is not None) and \
           (preview_window.buffer.name == path):
            self.vim.command('pclose!')
        else:
            prev_id = self.vim.call('win_getid')
            self.vim.call('denite#util#execute_path', 'pedit!', path)
            self.vim.command('wincmd P')
            self.__jump(context, target)
            self.vim.call('win_gotoid', prev_id)
        return True

    def get_preview_window(self):
        for id in range(0, len(self.vim.windows) - 1):
            if self.vim.call('getwinvar', id + 1, '&pvw') == 1:
                return self.vim.windows[id]
        return None

    def __jump(self, context, target):
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
