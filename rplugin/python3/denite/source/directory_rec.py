# ============================================================================
# FILE: directory_rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         okamos <himinato.k at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.process import Process


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'directory_rec'
        self.kind = 'directory'
        self.vars = {
            'command': []
        }

    def on_init(self, context):
        self.__proc = None
        directory = context['args'][0] if len(
            context['args']) > 0 else self.vim.call('getcwd')
        context['__directory'] = self.vim.call('expand', directory)

    def on_close(self, context):
        if self.__proc:
            self.__proc.kill()
            self.__proc = None

    def gather_candidates(self, context):
        if self.__proc:
            return self.__async_gather_candidates(context)

        if not self.vars['command']:
            self.vars['command'] = [
                'find', '-L', context['__directory'],
                '-path', '*/.git/*', '-prune', '-o',
                '-type', 'l', '-print', '-o', '-type', 'd', '-print']
        else:
            self.vars['command'].append(context['__directory'])
        self.__proc = Process(self.vars['command'],
                              context, context['__directory'])
        return self.__async_gather_candidates(context)

    def __async_gather_candidates(self, context):
        outs, errs = self.__proc.communicate(timeout=2.0)
        context['is_async'] = not self.__proc.eof()
        return [{'word': x + '/', 'action__path': x} for x in outs if x != '']
