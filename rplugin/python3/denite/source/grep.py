# ============================================================================
# FILE: grep.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import parse_jump_line
from denite.process import Process
import os
import shlex


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'grep'
        self.kind = 'jump_list'
        self.vars = {
            'command': ['grep'],
            'default_opts': ['-inH'],
            'recursive_opts': ['-r'],
            'separator': ['--'],
            'final_opts': ['.'],
        }
        self.__proc = None

    def on_init(self, context):
        directory = context['args'][0] if len(
            context['args']) > 0 else self.vim.call('getcwd')
        context['__arguments'] = context['args'][1:]
        context['__directory'] = self.vim.call('expand', directory)
        context['__input'] = self.vim.call('input',
                                           'Pattern: ', context['input'])

    def on_close(self, context):
        if self.__proc:
            self.__proc.kill()
            self.__proc = None

    def gather_candidates(self, context):
        if self.__proc:
            return self.__async_gather_candidates(context)

        if context['__input'] == '':
            return []

        commands = []
        commands += self.vars['command']
        commands += self.vars['default_opts']
        commands += self.vars['recursive_opts']
        commands += context['__arguments']
        commands += self.vars['separator']
        commands += shlex.split(context['__input'])
        commands += self.vars['final_opts']

        self.__proc = Process(commands, context['__directory'])
        context['is_async'] = True
        return self.__async_gather_candidates(context)

    def __async_gather_candidates(self, context):
        outs, errs = self.__proc.communicate(timeout=2.0)
        context['is_async'] = not self.__proc.eof()

        candidates = []

        for line in outs:
            result = parse_jump_line(context['__directory'], line)
            if result:
                candidates.append({
                    'word': '{0}:{1}{2}: {3}'.format(
                        os.path.relpath(result[0],
                                        start=context['__directory']),
                        result[1],
                        (': ' + result[2] if result[2] != '0' else ''),
                        result[3]),
                    'action__path': result[0],
                    'action__line': result[1],
                    'action__col': result[2],
                })
        return candidates
