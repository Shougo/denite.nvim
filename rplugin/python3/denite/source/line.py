# ============================================================================
# FILE: line.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base

LINE_NUMBER_SYNTAX = (
    'syntax match deniteSource_lineNumber '
    r'/\d\+\(:\d\+\)\?/ '
    'contained containedin=')
LINE_NUMBER_HIGHLIGHT = 'highlight default link deniteSource_lineNumber LineNR'


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'line'
        self.kind = 'file'
        self.matchers = ['matcher_regexp']
        self.sorters = []

    def on_init(self, context):
        context['__linenr'] = self.vim.current.window.cursor[0]
        context['__bufname'] = self.vim.current.buffer.name
        context['__bufnr'] = self.vim.current.buffer.number
        context['__direction'] = 'all'
        context['__fmt'] = '%' + str(len(
            str(self.vim.call('line', '$')))) + 'd: %s'
        if context['args'] and (context['args'][0] == 'all' or
                                context['args'][0] == 'forward' or
                                context['args'][0] == 'backward'):
            context['__direction'] = context['args'][0]

    def highlight(self):
        self.vim.command(LINE_NUMBER_SYNTAX + self.syntax_name)
        self.vim.command(LINE_NUMBER_HIGHLIGHT)

    def gather_candidates(self, context):
        linenr = context['__linenr']
        lines = [{'word': x,
                  'abbr': (context['__fmt'] % (i + 1, x)),
                  'action__path': context['__bufname'],
                  'action__line': (i + 1)}
                 for [i, x] in
                 enumerate(self.vim.call(
                     'getbufline', context['__bufnr'], 1, '$'))]
        if context['__direction'] == 'all':
            return lines
        elif context['__direction'] == 'backward':
            return list(reversed(lines[:linenr])) + list(
                reversed(lines[linenr:]))
        else:
            return lines[linenr-1:] + lines[:linenr-1]
