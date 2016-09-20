# ============================================================================
# FILE: grep.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import parse_jump_line
import subprocess
import os


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'grep'
        self.kind = 'jump_list'
        self.vars = {
            'command': ['grep'],
            'default_opts': ['-inH'],
            'recursive_opts': ['-r'],
            'separator': ['--'],
        }

    def on_init(self, context):
        directory = context['args'][0] if len(
            context['args']) > 0 else self.vim.call('getcwd')
        context['__directory'] = self.vim.call('expand', directory)
        context['__input'] = self.vim.call('input',
                                           'Pattern: ', context['input'])

    def gather_candidates(self, context):
        commands = []
        commands += self.vars['command']
        commands += self.vars['default_opts']
        commands += self.vars['recursive_opts']
        commands += self.vars['separator']
        commands += [context['__input']]
        commands += [context['__directory']]
        proc = subprocess.Popen(commands,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        try:
            outs, errs = proc.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()

        candidates = []
        for line in outs.decode('utf-8').split('\n'):
            result = parse_jump_line(self.vim, line)
            if result:
                candidates.append({
                    'word': '{0}: {1}{2}: {3}'.format(
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
