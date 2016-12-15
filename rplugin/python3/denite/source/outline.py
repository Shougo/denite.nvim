# ============================================================================
# FILE: outlint.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa _at_ gmail.com)
# License: MIT license
# ============================================================================

from .base import Base
from subprocess import check_output, CalledProcessError

OUTLINE_HIGHLIGHT_SYNTAX = [
    {'name': 'Line', 'link': 'Constant',   're': '\d\+'},
    {'name': 'Name', 'link': 'Identifier', 're': '\s\S\+\%(\s\+\[\)\@='},
    {'name': 'Type', 'link': 'Type',       're': '\[.\{-}\]'},
    {'name': 'Ref',  'link': 'Comment',    're': '\s\s.\+'}
]


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'outline'
        self.kind = 'file'
        self.syntax_name = 'deniteSource_outline'
        self.vars = {
            'command': ['ctags'],
            'options': ['-x'],
            'ignore_types': [],
            'encode': 'utf-8'
        }

    def on_init(self, context):
        context['__path'] = context['args'][0] if len(
            context['args']) > 0 else self.vim.current.buffer.name

    def highlight_syntax(self):
        for syn in OUTLINE_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {0}_{1} {2}'.format(
                    self.syntax_name, syn['name'], syn['link']))
        self.vim.command(
            'syntax region ' + self.syntax_name + ' start=// end=/$/ '
            'contains=deniteMatched contained')

    def gather_candidates(self, context):
        command = []
        command += self.vars['command']
        command += self.vars['options']
        command += [context['__path']]

        try:
            outline = check_output(command).decode(self.vars['encode'])
        except CalledProcessError:
            return []

        candidates = []
        for line in [l for l in outline.split('\n') if l != '']:
            info = self._parse_outline_info(line)
            if info['type'] not in self.vars['ignore_types']:
                candidates.append({
                    'word': '{line} {name} [{type}]  {ref}'.format(**info),
                    'action__path': context['__path'],
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
            'ref': ' '.join(elem[4:])
        }
