# ============================================================================
# FILE: file/rec_int.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import shutil

from pathlib import Path

from denite.base.source import Base
from denite.process import Process
from denite.util import abspath, Nvim, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file/rec_int'
        self.kind = 'file'
        self.vars = {
            'cache_command': [],
            'grep_command': ['grep'],
            'grep_default_opts': ['-inH'],
            'grep_final_opts': [],
            'grep_pattern_opt': ['-e'],
            'grep_recursive_opts': ['-r'],
            'grep_separator': ['--'],
        }
        self.converters = ['converter/truncate_abbr']

        self._cachepath: str = ''

    def on_init(self, context: UserContext) -> None:
        context['__proc'] = None
        directory = context['args'][0] if len(
            context['args']) > 0 else context['path']
        context['__directory'] = abspath(self.vim, directory)

    def on_close(self, context: UserContext) -> None:
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

    def gather_candidates(self, context: UserContext) -> Candidates:
        if not self.vars['cache_command']:
            self.error_message(context, 'cache_command is empty.')
            return []

        directory = context['__directory']
        if not Path(directory).is_dir():
            return []

        if context['__proc']:
            return self._async_gather_candidates(
                context, context['async_timeout'])

        args = self.vars['command'] + [directory]
        if shutil.which(args[0]) is None:
            self.error_message(context, args[0] + ' is not executable.')
            return []
        self.print_message(context, args)
        context['__proc'] = Process(args, context, directory)
        context['__current_candidates'] = []
        return self._async_gather_candidates(context, 0.5)

    def _async_gather_candidates(self, context: UserContext,
                                 timeout: float) -> Candidates:
        outs, errs = context['__proc'].communicate(timeout=timeout)
        if errs:
            self.error_message(context, errs)
        if not context['__proc']:
            return []

        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None
        if not outs:
            return []
        directory = context['__directory']
        if Path(outs[0]).is_absolute():
            candidates = [{
                'word': str(Path(x).relative_to(directory)),
                'action__path': x,
                } for x in outs if x != '' and directory in x]
        else:
            candidates = [{
                'word': x,
                'action__path': str(Path(directory).joinpath(x)),
                } for x in outs if x != '']
        context['__current_candidates'] += candidates

        return candidates
