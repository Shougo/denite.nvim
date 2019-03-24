# ============================================================================
# FILE: file/rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import argparse
import shutil
from sys import executable, base_exec_prefix
from pathlib import Path

from denite.base.source import Base
from denite.process import Process
from denite.util import parse_command, abspath


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file/rec'
        self.kind = 'file'
        self.vars = {
            'command': [],
            'cache_threshold': 10000,
        }
        self._cache = {}

    def on_init(self, context):
        """scantree.py command has special meaning, using the internal
        scantree.py Implementation"""

        if self.vars['command']:
            if self.vars['command'][0] == 'scantree.py':
                self.vars['command'] = self.parse_command_for_scantree(
                    self.vars['command'])
        else:
            if not context['is_windows']:
                self.vars['command'] = [
                    'find', '-L', ':directory',
                    '-path', '*/.git/*', '-prune', '-o',
                    '-type', 'l', '-print', '-o', '-type', 'f', '-print']
            else:
                self.vars['command'] = self.parse_command_for_scantree(
                    ['scantree.py'])

        context['__proc'] = None
        directory = context['args'][0] if len(
            context['args']) > 0 else context['path']
        context['__directory'] = abspath(self.vim, directory)

    def on_close(self, context):
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

    def gather_candidates(self, context):
        if not self.vars['command']:
            return []

        directory = context['__directory']
        if not Path(directory).is_dir():
            return []

        if context['is_redraw'] and directory in self._cache:
            self._cache.pop(directory)
        if directory in self._cache:
            return self._cache[directory]

        if context['__proc']:
            return self._async_gather_candidates(
                context, context['async_timeout'])

        if ':directory' in self.vars['command']:
            args = parse_command(
                self.vars['command'], directory=directory)
        else:
            args = self.vars['command'] + [directory]
        if shutil.which(args[0]) is None:
            self.error_message(context, args[0] + ' is not executable.')
            return []
        self.print_message(context, args)
        context['__proc'] = Process(args, context, directory)
        context['__current_candidates'] = []
        return self._async_gather_candidates(context, 0.5)

    def _async_gather_candidates(self, context, timeout):
        outs, errs = context['__proc'].communicate(timeout=timeout)
        if errs:
            self.error_message(context, errs)
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
                } for x in outs if x != '']
        else:
            candidates = [{
                'word': x,
                'action__path': str(Path(directory).joinpath(x)),
                } for x in outs if x != '']
        context['__current_candidates'] += candidates

        threshold = int(self.vars['cache_threshold'])
        if (not context['__proc'] and threshold > 0 and
                len(context['__current_candidates']) > threshold):
            self._cache[directory] = context['__current_candidates']

        return candidates

    @staticmethod
    def get_python_exe():
        if 'py' in str(Path(executable).name):
            return executable

        for exe in ['python3', 'python']:
            if shutil.which(exe) is not None:
                return shutil.which(exe)

        for name in (Path(base_exec_prefix).joinpath(v) for v in [
                'python3', 'python',
                str(Path('bin').joinpath('python3')),
                str(Path('bin').joinpath('python')),
        ]):
            if name.exists():
                return str(name)

        # return sys.executable anyway. This may not work on windows
        return executable

    def parse_command_for_scantree(self, cmd):
        """Given the user choice for --ignore get the corresponding value"""

        parser = argparse.ArgumentParser(description="parse scantree options")
        parser.add_argument('--ignore', type=str, default=None)

        # the first name on the list is 'scantree.py'
        args = parser.parse_args(
            cmd[1:] if cmd and cmd[0] == 'scantree.py' else cmd)
        if args.ignore is None:
            ignore = self.vim.options['wildignore']
        else:
            ignore = args.ignore

        scantree_py = Path(__file__).parent.parent.parent.joinpath(
            'scantree.py')

        return [Source.get_python_exe(), str(scantree_py), '--ignore', ignore,
                '--path', ':directory']
