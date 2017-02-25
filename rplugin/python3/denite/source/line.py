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

    def highlight(self):
        self.vim.command(LINE_NUMBER_SYNTAX + self.syntax_name)
        self.vim.command(LINE_NUMBER_HIGHLIGHT)

    def gather_candidates(self, context):
        fmt = '%' + str(len(str(self.vim.call('line', '$')))) + 'd: %s'

        lines = [{'word': x,
                  'abbr': (fmt % (i + 1, x)),
                  'action__path': context['__bufname'],
                  'action__line': (i + 1)}
                 for [i, x] in
                 enumerate(self.vim.call(
                     'getbufline', context['__bufnr'], 1, '$'))]
        return lines[context['__linenr']-1:] + lines[:context['__linenr']-1]
