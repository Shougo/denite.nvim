# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
import os
from itertools import filterfalse

from .openable import Kind as Openable
from denite.util import clearmatch


class Kind(Openable):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file'
        self.default_action = 'open'
        self.persist_actions += ['preview', 'highlight']
        self._previewed_target = {}

    def action_open(self, context):
        cwd = self.vim.call('getcwd')
        for target in context['targets']:
            path = target['action__path']
            match_path = '^{0}$'.format(path)

            if re.match('https?://', path):
                # URI
                self.vim.call('denite#util#open', path)
                return
            if path.startswith(cwd):
                path = os.path.relpath(path, cwd)

            if self.vim.call('bufwinnr', match_path) <= 0:
                self.vim.call(
                    'denite#util#execute_path', 'edit', path)
            elif self.vim.call('bufwinnr',
                               match_path) != self.vim.current.buffer:
                self.vim.command('buffer' +
                                 str(self.vim.call('bufnr', path)))
            self.__jump(context, target)

    def action_preview(self, context):
        target = context['targets'][0]

        if (not context['auto_preview'] and
                self.__get_preview_window() and
                self._previewed_target == target):
            self.vim.command('pclose!')
            return

        path = target['action__path'].replace('/./', '/')
        prev_id = self.vim.call('win_getid')
        self.vim.call('denite#helper#preview_file', context, path)
        self.vim.command('wincmd P')
        self.__jump(context, target)
        self.__highlight(context, int(target.get('action__line', 0)))
        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target

    def action_highlight(self, context):
        target = context['targets'][0]
        bufnr = self.vim.call('bufnr', target['action__path'])

        if not (self.vim.call('win_id2win', context['prev_winid']) and
                context['prev_winid'] in self.vim.call('win_findbuf', bufnr)):
            return

        prev_id = self.vim.call('win_getid')
        self.vim.call('win_gotoid', context['prev_winid'])
        self.__jump(context, target)
        self.__highlight(context, int(target.get('action__line', 0)))
        self.vim.call('win_gotoid', prev_id)

    def action_quickfix(self, context):
        qflist = [{
            'filename': x['action__path'],
            'lnum': x['action__line'],
            'text': x['action__text'],
        } for x in context['targets']
                  if 'action__line' in x and 'action__text' in x]
        self.vim.call('setqflist', qflist)
        self.vim.command('copen')

    def __highlight(self, context, line):
        clearmatch(self.vim)
        self.vim.current.window.vars['denite_match_id'] = self.vim.call(
            'matchaddpos', context['highlight_preview_line'], [line])

    def __get_preview_window(self):
        return next(filterfalse(lambda x:
                                not x.options['previewwindow'],
                                self.vim.windows), None)

    def __jump(self, context, target):
        if 'action__pattern' in target:
            self.vim.call('search', target['action__pattern'], 'w')

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

    # Needed for openable actions
    def __winid(self, target):
        path = target['action__path']
        bufnr = self.vim.call('bufnr', path)
        if bufnr == -1:
            return None
        winids = self.vim.call('win_findbuf', bufnr)
        return None if len(winids) == 0 else winids[0]
