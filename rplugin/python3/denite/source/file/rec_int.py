# ============================================================================
# FILE: file/rec_int.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import shutil

from pathlib import Path

from denite.base.source.interactive import Source as Base
from denite.process import Process
from denite.util import abspath, Nvim, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file/rec_int'
        self.kind = 'file'
        self.vars.update({
            'command': [],
            'grep_default_opts': ['-i'],
        })
        self.converters = ['converter/truncate_abbr']

        self._cache_path: str = ''
        self._cache_done: bool = False

    def on_init(self, context: UserContext) -> None:
        context['__proc'] = None
        directory = context['args'][0] if len(
            context['args']) > 0 else context['path']
        context['__directory'] = abspath(self.vim, directory)

        # Interactive mode
        context['is_interactive'] = True

        context['__args'] = ''

    def on_close(self, context: UserContext) -> None:
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

        path = Path(self._cache_path)
        if path.exists() and not path.is_dir():
            path.unlink()

    def gather_candidates(self, context: UserContext) -> Candidates:
        if not self.vars['command']:
            self.error_message(context, 'command is empty.')
            return []

        directory = context['__directory']
        if not Path(directory).is_dir():
            return []

        if context['__proc']:
            if not self._cache_done:
                self._cache_done = self._make_cache(
                    context, context['async_timeout'])
            if not self._cache_done:
                # Not cached yet
                return []

            args = self.init_grep_args(context)
            if args != context['__args'] or not context['__proc']:
                # Init grep commands
                context['__args'] = args
                self.print_message(context, str(args))
                context['__proc'] = Process(args, context, context['path'])

            return self._async_gather_candidates(context, 0.5)

        args = self.vars['command'] + [directory]
        if shutil.which(args[0]) is None:
            self.error_message(context, args[0] + ' is not executable.')
            return []

        self.print_message(context, args)
        context['__proc'] = Process(args, context, directory)
        context['is_async'] = True
        self._cache_path = self.vim.call('tempname')
        context['__path'] = self._cache_path
        self._cache_done = False
        self._make_cache(context, 0.5)
        return []

    def _make_cache(self, context: UserContext,
                    timeout: float) -> bool:
        outs, errs = context['__proc'].communicate(timeout=timeout)
        if errs:
            self.error_message(context, errs)
        if not context['__proc']:
            return False

        if outs:
            with open(self._cache_path, 'a') as f:
                f.write('\n'.join(outs))

        return bool(context['__proc'].eof())

    def _init_grep(self, context: UserContext) -> None:
        args = self.init_grep_args(context)

        if context.get('__proc'):
            context['__proc'].kill()
            context['__proc'] = None

        context['__args'] = args
        self.print_message(context, str(args))

        context['__proc'] = Process(args, context, context['path'])

    def _async_gather_candidates(self, context: UserContext,
                                 timeout: float) -> Candidates:
        outs, errs = context['__proc'].communicate(timeout=timeout)
        if errs:
            self.error_message(context, errs)
        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None

        candidates = []

        directory = context['__directory']
        if outs and Path(outs[0]).is_absolute():
            candidates = [{
                'word': str(Path(x).relative_to(directory)),
                'action__path': x,
                } for x in outs if x != '' and directory in x]
        else:
            candidates = [{
                'word': x,
                'action__path': str(Path(directory).joinpath(x)),
                } for x in outs if x != '']
        return candidates
