# ============================================================================
# FILE: file_rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.process import Process
from os.path import relpath


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
        self.__proc = None
        directory = context['args'][0] if len(
            context['args']) > 0 else context['directory']
        context['__directory'] = self.vim.call('expand', directory)

    def on_close(self, context):
        if self.__proc:
            self.__proc.kill()
            self.__proc = None

    def gather_candidates(self, context):
        if self.__proc:
            candidates = self.__async_gather_candidates(context, 0.5)
            return candidates

        directory = context['__directory']

        if directory in self.__cache and not context['is_redraw']:
            return self.__cache[directory]

        if not self.vars['command']:
            if context['is_windows']:
                return []

            self.vars['command'] = [
                'find', '-L', directory,
                '-path', '*/.git/*', '-prune', '-o',
                '-type', 'l', '-print', '-o', '-type', 'f', '-print']
        else:
            self.vars['command'].append(directory)
        self.__proc = Process(self.vars['command'],
                              context, directory)
        self.__current_candidates = []
        return self.__async_gather_candidates(context, 2.0)

    def __async_gather_candidates(self, context, timeout):
        outs, errs = self.__proc.communicate(timeout=timeout)
        context['is_async'] = not self.__proc.eof()
        candidates = [{'word': relpath(x, start=context['__directory']),
                 'action__path': x} for x in outs if x != '']
        self.__current_candidates += candidates
        if len(self.__current_candidates) >= self.vars['min_cache_files']:
            self.__cache[context['__directory']] = self.__current_candidates
        return candidates
