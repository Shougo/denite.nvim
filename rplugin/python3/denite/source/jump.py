# ============================================================================
# FILE: jump.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re

from denite.base.source import Base
from denite.util import relpath, Nvim, UserContext, Candidates

JUMP_HIGHLIGHT_SYNTAX = [
    {'name': 'File',     'link': 'Constant',   're': r'file: .*'},
    {'name': 'Text',     'link': 'Function',   're': r'text: .*'},
]


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'jump'
        self.kind = 'file'

    def highlight(self) -> None:
        for syn in JUMP_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def on_init(self, context: UserContext) -> None:
        if self.vim.call('exists', '*getjumplist'):
            jumps = self._get_jumplist(context)
        else:
            jumps = self._parse(context)
        context['__jumps'] = jumps[::-1]

    def _get_jumplist(self, context: UserContext) -> Candidates:
        [jump_info, pointer] = self.vim.call('getjumplist')
        jump_list: Candidates = []
        index = pointer + 1
        inc = -1
        for jump in jump_info:

            if index == 0:
                inc = 1

            index += inc
            lnum, col = jump['lnum'], jump['col']

            cur_buf = self.vim.current.buffer
            cur_bufnr = cur_buf.number
            jump_bufnr = jump['bufnr']
            jump_bufname = self.vim.buffers[jump_bufnr].name

            # TODO: if buf not loaded, it will get lnum 1
            if len(self.vim.buffers[jump_bufnr]) < lnum:
                jump_bufname = cur_buf.name
                jump_bufnr = cur_buf.number
                cur_pos = self.vim.call('getcurpos')
                lnum, col = cur_pos[1], cur_pos[2]
                file_or_text = '-invalid-'
            elif jump_bufnr == cur_bufnr:
                # cur_buf start with zero, so lnum - 1
                file_or_text = "text:" + cur_buf[lnum - 1]
            elif jump_bufnr != cur_bufnr:
                file_or_text = "file: " + jump_bufname

            if index == 0:
                word = '> {:>3} {:>5} {:>5} {}'.format(
                    index, lnum, col, file_or_text)
            else:
                word = '  {:>3} {:>5} {:>5} {}'.format(
                    index, lnum, col, file_or_text)

            jump_list.append({
                'word': word,
                'action__path': jump_bufname,
                'action__bufnr': jump_bufnr,
                'action__line': lnum,
                'action__col': col,
            })

        return jump_list

    def _parse(self, context: UserContext) -> Candidates:
        jump_list: Candidates = []

        for row_data in self.vim.call('execute', 'jumps').split('\n'):
            elements = row_data.split(maxsplit=3)

            if not elements:
                continue

            # If file/text is whitespace and it was deleted by split method
            # element[4] is file/text
            if len(elements) == 3:
                elements.append('')

            if elements[0] == '>' and len(elements) > 1:
                # skip the '>' sign
                elements = elements[1:]

                # split last element and concate
                # , because we just split three times
                last_element = elements[-1]
                elements = elements[:-1]
                elements.extend(last_element.split(maxsplit=1))

            file_text = elements[-1]

            # if '>' point nothing
            if elements[0] == '>' and len(elements) == 1:
                cur_pos = self.vim.call('getcurpos')
                lnum, col = cur_pos[1], cur_pos[2]
                path = self.vim.current.buffer.name
                word = row_data
            # if '>' point something, and first three filed is digit
            elif elements[0].isdigit() and elements[1].isdigit() and \
                    elements[2].isdigit():

                lnum, col = int(elements[1]), int(elements[2]) + 1

                file_text_is_path = False
                for b in self.vim.buffers:
                    rel_path = relpath(self.vim, b.name)
                    if rel_path == file_text.strip():
                        file_text_is_path = True
                        path = b.name
                        prefix = 'file: '
                        break

                if not file_text_is_path:
                    path = self.vim.current.buffer.name
                    prefix = 'text: ' if file_text != '-invalid-' else ''

                m = re.search(r'(^>*\s+\w+\s+\w+\s+\w+)', row_data)
                if not m:
                    continue
                word = m.group(0) + ' ' + prefix + file_text

            else:
                continue

            jump_list.append({
                'word': word,
                'action__path': self.vim.call('fnamemodify', path, ':p'),
                'action__line': lnum,
                'action__col': col,
            })
        return jump_list

    def gather_candidates(self, context: UserContext) -> Candidates:
        return context['__jumps']  # type: ignore
