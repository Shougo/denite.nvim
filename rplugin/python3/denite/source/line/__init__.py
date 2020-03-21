# ============================================================================
# FILE: line.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.source import Base
from denite.util import abspath, Nvim, UserContext, Candidates

LINE_NUMBER_SYNTAX = (
    'syntax match deniteSource_lineNumber '
    r'/\d\+\(:\d\+\)\?/ '
    'contained containedin=')
LINE_NUMBER_HIGHLIGHT = 'highlight default link deniteSource_lineNumber LineNR'


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'line'
        self.kind = 'file'
        self.matchers = ['matcher/regexp']
        self.sorters = []

    def on_init(self, context: UserContext) -> None:
        context['__linenr'] = self.vim.current.window.cursor[0]
        context['__bufnrs'] = [self.vim.current.buffer.number]
        context['__direction'] = 'all'
        context['__emptiness'] = 'empty'
        context['__fmt'] = '%' + str(len(
            str(self.vim.call('line', '$')))) + 'd: %s'
        argc = len(context['args'])

        direction = context['args'][0] if argc >= 1 else None
        if (direction == 'all' or direction == 'forward' or
                direction == 'backward'):
            context['__direction'] = direction
        elif direction == 'buffers':
            context['__bufnrs'] = [x.number for x in self.vim.buffers
                                   if x.options['buflisted']]
        elif direction == 'args':
            context['__bufnrs'] = [self.vim.call('bufnr', x) for x
                                   in self.vim.call('argv')]

        emptiness = context['args'][1] if argc >= 2 else None
        if emptiness == 'noempty':
            context['__emptiness'] = emptiness

    def highlight(self) -> None:
        self.vim.command(LINE_NUMBER_SYNTAX + self.syntax_name)
        self.vim.command(LINE_NUMBER_HIGHLIGHT)

    def gather_candidates(self, context: UserContext) -> Candidates:
        linenr = context['__linenr']
        candidates: Candidates = []
        for bufnr in context['__bufnrs']:
            lines = [{
                'word': x,
                'abbr': (context['__fmt'] % (i + 1, x)),
                'action__path': abspath(self.vim,
                                        self.vim.current.buffer.name),
                'action__bufnr': bufnr,
                'action__col': 0,
                'action__line': (i + 1),
                'action__text': x,
            } for [i, x] in enumerate(
                self.vim.call('getbufline', bufnr, 1, '$'))]
            if context['__emptiness'] == 'noempty':
                lines = list(filter(lambda c: c['word'] != '', lines))
            if context['__direction'] == 'all':
                candidates += lines
            elif context['__direction'] == 'backward':
                candidates += list(reversed(lines[:linenr])) + list(
                    reversed(lines[linenr:]))
            else:
                candidates += lines[linenr-1:] + lines[:linenr-1]
        return candidates
