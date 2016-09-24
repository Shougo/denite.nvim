# ============================================================================
# FILE: ack.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         Luis Carlos Cruz Carballo <lcruzc at linkux-it.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import parse_jump_line
import subprocess
import os


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'ack'
        self.kind = 'jump_list'
        self.vars = {
            'command': 'ack',
            'default_opts': '-s -H --nopager --nocolor --nogroup --column',
        }

    def on_init(self, context):
        directory = context['args'][0] if len(
            context['args']) > 0 else self.vim.call('getcwd')
        context['__directory'] = self.vim.call('expand', directory)
        context['__input'] = self.vim.call('input',
                                           'Ack query: ', context['input'])

    def gather_candidates(self, context):
        if context['__input'] == '':
            return []

        command = '{0} {1} {2}'.format(
            self.vars['command'],
            self.vars['default_opts'],
            context['__input']
        )
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True,
                                cwd=context['__directory'])
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
