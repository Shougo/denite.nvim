# ============================================================================
# FILE: change.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from denite.base.source import Base
from denite.util import Nvim, UserContext, Candidates

CHANGE_HIGHLIGHT_SYNTAX = [
    {'name': 'Text', 'link': 'Function', 're': r'\v(\d+\s+\d+\s+\d+\s+)\zs.*'},
]


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'change'
        self.kind = 'file'

    def on_init(self, context: UserContext) -> None:
        context['__parse'] = self._parse(context)[::-1]

    def highlight(self) -> None:
        for syn in CHANGE_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def _parse(self, context: UserContext) -> typing.List[
            typing.Dict[str, typing.Any]]:
        change_list = []
        for row_data in self.vim.call('execute', 'changes').split('\n'):
            elements = row_data.split()

            if [] == elements:
                continue

            # skip the '>' sign
            if elements[0] == '>' and len(elements) > 1:
                elements = elements[1:]

            # if '>' point nothing
            if elements[0] == '>' and len(elements) == 1:
                cur_pos = self.vim.call('getcurpos')
                lnum, col = cur_pos[1], cur_pos[2]
            # if '>' point something, and first three filed is digit
            elif elements[0].isdigit() and elements[1].isdigit and \
                    elements[2].isdigit():
                lnum, col = int(elements[1]), int(elements[2]) + 1
            else:
                continue

            change_list.append({
                'word': row_data,
                'action__path': self.vim.current.buffer.name,
                'action__line': lnum,
                'action__col': col,
            })

        return change_list

    def gather_candidates(self, context: UserContext) -> Candidates:
        return context['__parse']  # type: ignore
