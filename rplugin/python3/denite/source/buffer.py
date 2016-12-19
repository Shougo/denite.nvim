# ============================================================================
# FILE: buffer.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa@gmail.com)
# License: MIT license
# ============================================================================

from .base import Base
from os.path import getatime, exists
from time import localtime, strftime, time
from sys import maxsize

BUFFER_HIGHLIGHT_SYNTAX = [
    {'name': 'Name',     'link': 'Function',  're': '[^/ \[\]]\+\s'},
    {'name': 'Prefix',   'link': 'Constant',  're': '\d\+\s\+\%(\S\+\)\?'},
    {'name': 'Info',     'link': 'PreProc',   're': '\[.\{-}\] '},
    {'name': 'Modified', 'link': 'Statement', 're': '\[.\{-}+\]'},
    {'name': 'NoFile',   'link': 'Function',  're': '\[nofile\]'},
    {'name': 'Time',     'link': 'Statement', 're': '(.\{-})$'},
]


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'buffer'
        self.kind = 'buffer'
        self.vars = {
            'date_format': '%d %b %Y %H:%M:%S',
            'exclude_unlisted': 1,
            'exclude_filetypes': ['denite']
        }

    def on_init(self, context):
        self.__exclude_unlisted = \
            '!' not in context['args'] and self.vars['exclude_unlisted']
        self.__caller_bufnr = context['bufnr']
        self.__alter_bufnr = self.vim.call('bufnr', '#')

    def highlight(self):
        for syn in BUFFER_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {0}_{1} {2}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def gather_candidates(self, context):
        candidates = [
            self._convert(ba) for ba in [
                bufattr for bufattr in [
                    self._get_attributes(buf) for buf in self.vim.buffers
                ] if not self._is_excluded(bufattr)
            ]
        ]
        return sorted(candidates, key=(
            lambda x:
            maxsize if self.__caller_bufnr == x['bufnr']
            else -maxsize if self.__alter_bufnr == x['bufnr']
            else x['timestamp']))

    def _is_excluded(self, buffer_attr):
        if self.__exclude_unlisted and buffer_attr['status'][0] == 'u':
            return True
        if buffer_attr['filetype'] in self.vars['exclude_filetypes']:
            return True
        return False

    def _convert(self, buffer_attr):
        return {
            'bufnr': buffer_attr['number'],
            'word': '{0}{1} {2}{3} ({4})'.format(
                str(buffer_attr['number']).rjust(
                    len('{}'.format(len(self.vim.buffers))) + 1, ' '),
                buffer_attr['status'],
                self.vim.call('fnamemodify', buffer_attr['name'], ':~:.')
                if buffer_attr['name'] != '' else 'No Name',
                ' [{}]'.format(
                    buffer_attr['filetype']
                ) if buffer_attr['filetype'] != '' else '',
                strftime(self.vars['date_format'],
                         localtime(buffer_attr['timestamp']))
            ),
            'action__bufnr': buffer_attr['number'],
            'timestamp': buffer_attr['timestamp']
        }

    def _get_attributes(self, buf):
        attr = {
            'number': buf.number,
            'name': buf.name
        }

        attr.update({
            'filetype': buf.options['filetype'],
            'timestamp': getatime(
                attr['name']) if exists(attr['name']) else time(),
            'status': '{0}{1}{2}{3}'.format(
                ' ' if self.vim.call('buflisted', attr['number']) else 'u',
                '%' if attr['number'] == self.__caller_bufnr
                    else '#' if attr['number'] == self.__alter_bufnr else ' ',
                'a' if self.vim.call('bufwinnr', attr['number']) > 0
                    else 'h' if self.vim.call('bufloaded',
                                              attr['number']) != 0 else ' ',
                '=' if buf.options['readonly']
                    else ('+' if buf.options['modified']
                          else '-' if buf.options['modifiable'] == 0 else ' ')
            )
        })

        return attr
