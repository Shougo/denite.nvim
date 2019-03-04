# ============================================================================
# FILE: outline.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa _at_ gmail.com)
# License: MIT license
# ============================================================================

from subprocess import check_output, CalledProcessError
import re
import tempfile

from denite.source.base import Base
from denite.util import parse_tagline


OUTLINE_HIGHLIGHT_SYNTAX = [
    {'name': 'Name', 'link': 'Identifier', 're': r'\S\+\%(\s\+\[\)\@='},
    {'name': 'Type', 'link': 'Type',       're': r'\[.\{-}\]'},
    {'name': 'Ref',  'link': 'Comment',    're': r'\s\s.\+'}
]


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'outline'
        self.kind = 'file'
        self.vars = {
            'command': ['ctags'],
            'options': [],
            'file_opt': '-o',
            'ignore_types': [],
            'encoding': 'utf-8'
        }

    def on_init(self, context):
        context['__path'] = context['args'][0] if len(
            context['args']) > 0 else self.vim.current.buffer.name

    def highlight(self):
        for syn in OUTLINE_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def gather_candidates(self, context):
        with tempfile.NamedTemporaryFile(
                mode='w', encoding=self.vars['encoding']) as tf:
            args = []
            args += self.vars['command']
            args += self.vars['options']
            args += [self.vars['file_opt'], tf.name]
            args += [context['__path']]
            self.print_message(context, args)
            tf.close()

            try:
                check_output(args).decode(self.vars['encoding'], 'replace')
            except CalledProcessError:
                return []

            candidates = []
            with open(tf.name, encoding=self.vars['encoding'],
                      errors='replace') as f:
                for line in f:
                    if re.match('!', line) or not line:
                        continue
                    info = parse_tagline(line.rstrip(), tf.name)
                    candidate = {
                        'word': info['name'],
                        'action__path': info['file'],
                    }
                    fmt = '{name} [{type}] {file} {ref}'
                    candidate['abbr'] = fmt.format(**info)
                    if info['line']:
                        candidate['action__line'] = info['line']
                    else:
                        candidate['action__pattern'] = info['pattern']
                    candidates.append(candidate)
        return candidates
