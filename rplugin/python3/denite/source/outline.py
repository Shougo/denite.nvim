# ============================================================================
# FILE: buffer.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa _at_ gmail.com)
# License: MIT license
# ============================================================================

from .base import Base
from subprocess import check_output, CalledProcessError


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'outline'
        self.kind = 'file'
        self.vars = {
            'encode': ['utf-8'],
            'sort': ['no'],
            'ignore_types': []
        }

    def on_init(self, context):
        context['__bufname'] = context['args'][0] if len(
            context['args']) > 0 else self.vim.current.buffer.name

    def gather_candidates(self, context):
        command = ['ctags', '-x', context['__bufname'], '--sort=no']
        try:
            outline = check_output(command).decode(self.vars['encode'][0])
        except CalledProcessError:
            return []

        candidates = []
        for line in [l for l in outline.split('\n') if l != '']:
            info = self._parse_outline_info(line)
            if info['type'] not in self.vars['ignore_types']:
                candidates.append({
                    'word': '{line} {name} {type} :: {decl}'.format(**info),
                    'action__path': context['__bufname'],
                    'action__line': info['line']
                })
        return candidates

    def _parse_outline_info(self, line):
        elem = [e for e in line.split(' ') if e != '']
        return {
            'name': elem[0],
            'type': elem[1],
            'line': int(elem[2]),
            'file': elem[3],
            'decl': ' '.join(elem[4:])
        }
