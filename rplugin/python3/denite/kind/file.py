# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
import os
from itertools import filterfalse

from .openable import Kind as Openable
from denite import util


class Kind(Openable):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file'
        self.default_action = 'open'
        self.persist_actions += ['preview', 'highlight']
        self._previewed_target = {}
        self._previewed_buffers = {}

    def action_open(self, context):
        self._open(context, 'edit')

    def action_drop(self, context):
        self._open(context, 'drop')

    def action_new(self, context):
        path = util.input(self.vim, context, 'New file: ', completion='file')
        if not path:
            return
        context['targets'] = [{
            'word': path,
            'action__path': util.abspath(self.vim, path),
        }]
        self.action_open(context)

    def action_preview(self, context):
        target = context['targets'][0]

        if (not context['auto_preview'] and
                self._get_preview_window() and
                self._previewed_target == target):
            self.vim.command('pclose!')
            return

        listed = self.vim.call('buflisted', target['action__path'])
        path = target['action__path'].replace('/./', '/')
        prev_id = self.vim.call('win_getid')

        self.vim.call('denite#helper#preview_file', context, path)
        self.vim.command('wincmd P')

        if not listed:
            self._previewed_buffers[
                target['action__path']] = self.vim.call('bufnr', '%')
        self._jump(context, target)
        self._highlight(context, int(target.get('action__line', 0)))

        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target

        self._cleanup()

    def action_highlight(self, context):
        target = context['targets'][0]
        bufnr = self.vim.call('bufnr', target['action__path'])

        if not (self.vim.call('win_id2win', context['prev_winid']) and
                context['prev_winid'] in self.vim.call('win_findbuf', bufnr)):
            return

        prev_id = self.vim.call('win_getid')
        self.vim.call('win_gotoid', context['prev_winid'])
        self._jump(context, target)
        self._highlight(context, int(target.get('action__line', 0)))
        self.vim.call('win_gotoid', prev_id)

    def action_quickfix(self, context):
        qflist = [{
            'filename': x['action__path'],
            'lnum': x['action__line'],
            'col': x['action__col'],
            'text': x['action__text'],
        } for x in context['targets']
                  if 'action__line' in x and 'action__text' in x]
        self.vim.call('setqflist', qflist)
        self.vim.command('copen')

    def _open(self, context, command):
        cwd = self.vim.call('getcwd')
        for target in context['targets']:
            path = target['action__path']
            match_path = '^{0}$'.format(path)

            if re.match('https?://', path):
                # URI
                self.vim.call('denite#util#open', path)
                continue
            if path.startswith(cwd):
                path = os.path.relpath(path, cwd)

            if self.vim.call('bufwinnr', match_path) <= 0:
                self.vim.call(
                    'denite#util#execute_path', command, path)
            elif self.vim.call('bufwinnr',
                               match_path) != self.vim.current.buffer:
                self.vim.command('buffer' +
                                 str(self.vim.call('bufnr', path)))
            self._jump(context, target)

            if path in self._previewed_buffers:
                self._previewed_buffers.pop(path)

    def _cleanup(self):
        for bufnr in self._previewed_buffers.values():
            if not self.vim.call('win_findbuf', bufnr) and self.vim.call(
                    'buflisted', bufnr):
                self.vim.command('silent bdelete ' + str(bufnr))

    def _highlight(self, context, line):
        util.clearmatch(self.vim)
        self.vim.current.window.vars['denite_match_id'] = self.vim.call(
            'matchaddpos', context['highlight_preview_line'], [line])

    def _get_preview_window(self):
        return next(filterfalse(lambda x:
                                not x.options['previewwindow'],
                                self.vim.windows), None)

    def _jump(self, context, target):
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
    def _winid(self, target):
        path = target['action__path']
        bufnr = self.vim.call('bufnr', path)
        if bufnr == -1:
            return None
        winids = self.vim.call('win_findbuf', bufnr)
        return None if len(winids) == 0 else winids[0]
