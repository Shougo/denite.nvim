# ============================================================================
# FILE: buffer.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa@gmail.com)
# License: MIT license
# ============================================================================

from os.path import getatime, exists
from time import localtime, strftime, time
from sys import maxsize

from denite.base.source import Base

BUFFER_HIGHLIGHT_SYNTAX = [
    {'name': 'Name',     'link': 'Function',  're': r'[^/ \[\]]\+\s'},
    {'name': 'Prefix',   'link': 'Constant',  're': r'\d\+\s[\ ahu%#]\+\s'},
    {'name': 'Info',     'link': 'PreProc',   're': r'\[.\{-}\] '},
    {'name': 'Modified', 'link': 'Statement', 're': r'+\s'},
    {'name': 'NoFile',   'link': 'Function',  're': r'\[nofile\]'},
    {'name': 'Time',     'link': 'Statement', 're': r'(.\{-})'},
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
        context['__exclude_unlisted'] = ('!' not in context['args'] and
                                         self.vars['exclude_unlisted'])
        context['__caller_bufnr'] = context['bufnr']
        context['__alter_bufnr'] = self.vim.call('bufnr', '#')

    def highlight(self):
        for syn in BUFFER_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def gather_candidates(self, context):
        rjust = len(f'{len(self.vim.buffers)}') + 1
        ljustnm = 0
        rjustft = 0
        bufattrs = []
        for ba in [self._get_attributes(context, x)
                   for x in self.vim.buffers]:
            if not self._is_excluded(context, ba):
                if ba['name'] == '':
                    ba['fn'] = 'No Name'
                    ba['path'] = ''
                else:
                    ba['fn'] = self.vim.call('fnamemodify', ba['name'], ':~:.')
                    ba['path'] = self.vim.call('fnamemodify', ba['name'], ':p')
                ljustnm = max(ljustnm, len(ba['fn']))
                rjustft = max(rjustft, len(ba['filetype']))
                bufattrs.append(ba)
        candidates = [self._convert(x, rjust, ljustnm, rjustft)
                      for x in bufattrs]
        return sorted(candidates, key=(
            lambda x:
            maxsize if context['__caller_bufnr'] == x['bufnr']
            else -maxsize if context['__alter_bufnr'] == x['bufnr']
            else x['timestamp']))

    def _is_excluded(self, context, buffer_attr):
        if context['__exclude_unlisted'] and buffer_attr['status'][0] == 'u':
            return True
        if buffer_attr['filetype'] in self.vars['exclude_filetypes']:
            return True
        return False

    def _convert(self, buffer_attr, rjust, ljustnm, rjustft):
        return {
            'bufnr': buffer_attr['number'],
            'word': buffer_attr['fn'],
            'abbr': '{}{} {}{} {}'.format(
                str(buffer_attr['number']).rjust(rjust, ' '),
                buffer_attr['status'],
                buffer_attr['fn'].ljust(ljustnm, ' '),
                (f' [{buffer_attr["filetype"]}]'
                 if buffer_attr['filetype'] != '' else '').rjust(rjustft+3),
                strftime('(' + self.vars['date_format'] + ')',
                         localtime(buffer_attr['timestamp'])
                         ) if self.vars['date_format'] != '' else ''
            ),
            'action__bufnr': buffer_attr['number'],
            'action__path': buffer_attr['path'],
            'timestamp': buffer_attr['timestamp']
        }

    def _get_attributes(self, context, buf):
        attr = {
            'number': buf.number,
            'name': buf.name
        }

        attr.update({
            'filetype': self.vim.call('getbufvar', buf.number, '&filetype'),
            'timestamp': getatime(
                attr['name']) if exists(attr['name']) else time(),
            'status': '{}{}{}{}'.format(
                ' ' if self.vim.call('buflisted', attr['number'])
                    else 'u',
                '%' if attr['number'] == context['__caller_bufnr']
                    else '#' if attr['number'] == context['__alter_bufnr']
                    else ' ',
                'a' if self.vim.call('win_findbuf', attr['number'])
                    else 'h' if self.vim.call('bufloaded', attr['number']) != 0
                    else ' ',
                '=' if buf.options['readonly']
                    else '+' if buf.options['modified']
                    else '-' if buf.options['modifiable'] == 0
                    else ' '
            )
        })

        return attr
