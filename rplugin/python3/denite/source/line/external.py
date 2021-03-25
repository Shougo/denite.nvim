# ============================================================================
# FILE: line/external.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
from pynvim import Nvim
import typing

from denite.base.source.interactive import Source as Base
from denite.util import UserContext, Candidates, Candidate
from denite import util, process

LINE_NUMBER_SYNTAX = (
    'syntax match deniteSource_lineNumber '
    r'/\d\+\(:\d\+\)\?/ '
    'contained containedin=')
LINE_NUMBER_HIGHLIGHT = 'highlight default link deniteSource_lineNumber LineNR'


def _candidate(result: typing.List[typing.Any],
               bufnr: int, fmt: str) -> Candidate:
    return {
        'word': result[3],
        'abbr': fmt % (int(result[1]), result[3]),
        'action__bufnr': bufnr,
        'action__line': result[1],
        'action__col': result[2],
        'action__text': result[3],
    }


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'line/external'
        self.kind = 'file'
        self.sorters = []

    def on_init(self, context: UserContext) -> None:
        buf = self.vim.current.buffer

        context['__bufnr'] = buf.number
        context['__fmt'] = '%' + str(len(
            str(self.vim.call('line', '$')))) + 'd: %s'

        bufpath = util.abspath(self.vim, buf.name)
        context['__temp'] = ''
        if (buf.options['modified'] or 'nofile' in buf.options['buftype'] or
                not self.vim.call('filereadable', bufpath)):
            context['__temp'] = self.vim.call(
                'denite#helper#_get_temp_file', buf.number)
            context['__path'] = context['__temp']
        else:
            context['__path'] = bufpath

        # Interactive mode
        context['is_interactive'] = True

        context['__args'] = ''

    def on_close(self, context: UserContext) -> None:
        if context.get('__proc'):
            context['__proc'].kill()
            context['__proc'] = None

        if not context['__temp']:
            return

        path = Path(context['__temp'])
        if path.exists() and not path.is_dir():
            path.unlink()

    def highlight(self) -> None:
        self.vim.command(LINE_NUMBER_SYNTAX + self.syntax_name)
        self.vim.command(LINE_NUMBER_HIGHLIGHT)

    def gather_candidates(self, context: UserContext) -> Candidates:
        if not context['input']:
            return []

        args = self.init_grep_args(context)
        if args == context['__args'] and context['__proc']:
            return self._async_gather_candidates(context, 0.5)

        if context.get('__proc'):
            context['__proc'].kill()
            context['__proc'] = None

        context['__args'] = args
        self.print_message(context, str(args))

        context['__proc'] = process.Process(args, context, context['path'])
        return self._async_gather_candidates(context, 0.5)

    def _async_gather_candidates(self, context: UserContext,
                                 timeout: float) -> Candidates:
        outs, errs = context['__proc'].communicate(timeout=timeout)
        if errs:
            self.error_message(context, errs)
        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None

        candidates = []

        for line in outs:
            result = util.parse_jump_line(context['path'], line)
            if not result:
                continue
            candidates.append(_candidate(
                result, context['__bufnr'], context['__fmt']))
        return candidates
