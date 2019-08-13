
# ============================================================================
# FILE: mark.py
# AUTHOR: amikai (as23041248@gmail.com)
# License: MIT license
# ============================================================================

import typing

from denite.base.source import Base
from denite.kind.file import Kind as File
from denite.util import Nvim, UserContext, Candidates, Candidate


MARK_HIGHLIGHT_SYNTAX = [
    # \s\+\w
    {'name': 'Mark',     'link': 'Statement',
        're': r'\s\+[a-zA-z1-9\'"]\(\s\+\w\+\s\+\w\+\s\+\w\+\)\@='},
    {'name': 'File',     'link': 'Constant',   're': r'file: .*'},
    {'name': 'Text',     'link': 'Function',   're': r'text: .*'},
]


class Source(Base):

    def __init__(self,  vim: Nvim) -> None:
        super().__init__(vim)
        self.name = 'mark'
        self.kind = Kind(vim)

    def highlight(self) -> None:
        for syn in MARK_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def _get_marks(self, context: UserContext) -> Candidates:
        # see :help mark-motions
        # file marks
        lower_marks = [chr(c) for c in range(ord('a'), ord('z'))]
        upper_marks = [chr(c) for c in range(ord('A'), ord('Z'))]
        num_marks = [str(n) for n in range(1, 10)]
        others_marks = ['\'', '`', '\"', '[', ']', '^', '.', '<', '>']

        mark_list: Candidates = []

        # mark order same as :marks
        for m in [others_marks[0]] + lower_marks + \
                upper_marks + num_marks + others_marks[1:]:

            mark_info = [bufnum, lnum, col, off] = self.vim.call(
                'getpos', '\'' + m)
            if self.empty_mark(mark_info):
                continue

            bufname = self.vim.call('bufname',
                                    bufnum if bufnum != 0 else '%')
            path = self.vim.call('fnamemodify', bufname, ':p')
            if bufnum == 0:
                file_or_text = 'text: ' + self.vim.call('getline', lnum)
            else:
                file_or_text = 'file: ' + path

            mark_list.append({
                'word': '{:>3} {:>5} {:>5}  {}'
                .format(m, lnum, col, file_or_text),
                'action__path': path,
                'action__line': lnum,
                'action__col': col,
                'mark': m,
            })
        return mark_list

    def gather_candidates(self, context: UserContext) -> Candidates:
        return self._get_marks(context)

    def empty_mark(self, mark_info: typing.List[str]) -> bool:
        return mark_info[1] == 0 and \
            mark_info[2] == 0 and \
            mark_info[3] == 0


class Kind(File):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'mark'
        self._previewed_target: Candidate = {}

    def action_delete(self, context: UserContext) -> None:
        mark = context['targets'][0]['mark']

        # ' mark cannot delete
        if mark == '\'':
            return

        self.vim.command('delmarks ' + mark)
