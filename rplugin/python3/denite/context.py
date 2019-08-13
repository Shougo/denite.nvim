# ============================================================================
# FILE: context.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing
from pathlib import PurePath

from denite.util import Nvim

UserContext = typing.Dict[str, typing.Any]


class Context(object):

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim
        self._context: UserContext = {}

    def get(self, user_context: UserContext) -> UserContext:
        buffer_name = user_context.get('buffer_name', 'default')
        context = self._internal_options()
        context.update(self._vim.call('denite#init#_user_options'))
        context['custom'] = self._vim.call('denite#custom#_get')
        option = context['custom']['option']
        if '_' in option:
            context.update(option['_'])
        if buffer_name in option:
            context.update(option[buffer_name])
        context.update(user_context)

        if context['command'] == 'DeniteCursorWord':
            context['input'] = self._vim.call('expand', '<cword>')
        elif context['command'] == 'DeniteBufferDir':
            context['path'] = self._vim.call('expand', '%:p:h')
        elif context['command'] == 'DeniteProjectDir':
            context['path'] = self._vim.call(
                'denite#project#path2project_directory',
                context['path'], context['root_markers']
            )

        # Add buffer name to context
        bufname = PurePath(self._vim.current.buffer.name)
        try:
            context['bufname'] = str(bufname.relative_to(context['path']))
        except ValueError:
            context['bufname'] = bufname.name

        # For compatibility
        for [old_option, new_option] in [
                x for x in self._vim.call(
                    'denite#init#_deprecated_options').items()
                if x[0] in context and x[1]]:
            context[new_option] = context[old_option]

        return context

    def _internal_options(self) -> UserContext:
        return {
            'bufnr': self._vim.current.buffer.number,
            'command': '',
            'encoding': self._vim.options['encoding'],
            'error_messages': [],
            'firstline': 0,
            'filetype': self._vim.current.buffer.options['filetype'],
            'lastline': 0,
            'is_windows': (self._vim.call('has', 'win32') or
                           self._vim.call('has', 'win64')),
            'messages': [],
            'prev_winid': self._vim.call('win_getid'),
            'has_preview_window': len(
                [x for x in range(1, self._vim.call('winnr', '$'))
                 if self._vim.call('getwinvar', x, '&previewwindow')]) > 0,
            'quick_move_table': {
                'a': 0, 's': 1, 'd': 2, 'f': 3, 'g': 4,
                'h': 5, 'j': 6, 'k': 7, 'l': 8, ';': 9,
                'q': 10, 'w': 11, 'e': 12, 'r': 13, 't': 14,
                'y': 15, 'u': 16, 'i': 17, 'o': 18, 'p': 19,
                '1': 20, '2': 21, '3': 22, '4': 23, '5': 24,
                '6': 25, '7': 26, '8': 27, '9': 28, '0': 29,
            },
            'runtimepath': self._vim.options['runtimepath'],
            'selected_icon': '*',
        }
