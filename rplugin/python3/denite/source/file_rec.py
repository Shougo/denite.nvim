# ============================================================================
# FILE: file_rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.process import Process
from os import path, pardir
from os.path import relpath, isabs, isdir, join
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
        if not context['is_windows'] and not self.vars['command']:
            self.vars['command'] = [
                'find', '-L', ':directory',
                '-path', '*/.git/*', '-prune', '-o',
                '-type', 'l', '-print', '-o', '-type', 'f', '-print']

        if context['is_windows'] and not self.vars['command']:
            scantree = join(path.split(__file__)[0], pardir, 'scantree.py')
            self.vars['command'] = ['python', scantree, ':directory']

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
        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None
        if not outs:
            return []
        if isabs(outs[0]):
            candidates = [{'word': relpath(x, start=context['__directory']),
                           'action__path': x}
                          for x in outs if x != '']
        else:
            candidates = [{'word': x, 'action__path':
                           join(context['__directory'], x)}
                          for x in outs if x != '']
        context['__current_candidates'] += candidates
        if (len(context['__current_candidates']) >=
                self.vars['min_cache_files']):
            self.__cache[context['__directory']] = context[
                '__current_candidates']
        return candidates
