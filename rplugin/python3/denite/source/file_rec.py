# ============================================================================
# FILE: file_rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
import subprocess


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'file_rec'
        self.kind = 'jump_list'
        self.vars = {
            'command': []
        }
        self.__proc = None

    def on_init(self, context):
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
                '-type', 'l', '-print', '-o', '-type', 'f', '-print']
        else:
            self.vars['command'].append(context['__directory'])
        self.__proc = subprocess.Popen(self.vars['command'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        context['is_async'] = True

        return self.__async_gather_candidates(context)

    def __async_gather_candidates(self, context):
        try:
            outs, errs = self.__proc.communicate(timeout=0.1)
            context['is_async'] = False
        except subprocess.TimeoutExpired:
            return []
        return [{'word': x, 'action__path': x}
                for x in outs.decode('utf-8').split('\n') if x != '']
