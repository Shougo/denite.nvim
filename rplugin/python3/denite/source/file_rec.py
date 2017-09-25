# ============================================================================
# FILE: file_rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import argparse
import shutil
from .base import Base
from denite.process import Process
from os import path, pardir
from os.path import relpath, isabs, isdir, join, normpath
from denite.util import parse_command, abspath


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file_rec'
        self.kind = 'file'
        self.vars = {
            'command': [],
            'min_cache_files': 10000,
        }
        self.__cache = {}

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

        if context['__proc']:
            return self.__async_gather_candidates(
                context, context['async_timeout'])

        if context['is_redraw']:
            self.__cache = {}

        directory = context['__directory']
        if not isdir(directory):
            return []

        if directory in self.__cache:
            return self.__cache[directory]

        if ':directory' in self.vars['command']:
            args = parse_command(
                self.vars['command'], directory=directory)
        else:
            args = self.vars['command'] + [directory]
        self.print_message(context, args)
        context['__proc'] = Process(args, context, directory)
        context['__current_candidates'] = []
        return self.__async_gather_candidates(context, 0.5)

    def __async_gather_candidates(self, context, timeout):
        outs, errs = context['__proc'].communicate(timeout=timeout)
        if errs:
            self.error_message(errs)
        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None
        if not outs:
            return []
        if isabs(outs[0]):
            candidates = [{
                'word': relpath(x, start=context['__directory']),
                'action__path': x,
                } for x in outs if x != '']
        else:
            candidates = [{
                'word': x,
                'action__path': join(context['__directory'], x),
                } for x in outs if x != '']
        context['__current_candidates'] += candidates
        if (len(context['__current_candidates']) >=
                self.vars['min_cache_files']):
            self.__cache[context['__directory']] = context[
                '__current_candidates']
        return candidates

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

        current_folder, _ = path.split(__file__)
        scantree_py = normpath(join(current_folder, pardir, 'scantree.py'))

        if shutil.which('python3') is not None:
            python_exe = 'python3'
        else:
            python_exe = 'python'
        if shutil.which(python_exe) is None:
            raise FileNotFoundError("Coudn't find {} executable!".format(
                                    python_exe))

        return [python_exe, scantree_py, '--ignore', ignore,
                '--path', ':directory']
