# ============================================================================
# FILE: outline.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa _at_ gmail.com)
# License: MIT license
# ============================================================================

import re
import tempfile
from pathlib import Path
from subprocess import CalledProcessError, check_output

from denite.base.source import Base
from denite.util import parse_tagline

OUTLINE_HIGHLIGHT_SYNTAX = [
    {'name': 'Type', 'link': 'Statement', 're': r'\[.\{-}\]'},
    {'name': 'File', 'link': 'Type', 're': r'@\w*\W\w*'},
    {'name': 'Pattern', 'link': 'Comment', 're': r'<->\s.*'},
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
            'encoding': 'utf-8',
        }

    def on_init(self, context):
        context['__path'] = (
            context['args'][0]
            if len(context['args']) > 0
            else self.vim.current.buffer.name
        )

    def highlight(self):
        for syn in OUTLINE_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']
                )
            )
            self.vim.command(
                'highlight default link {0}_{1} {2}'.format(
                    self.syntax_name, syn['name'], syn['link']
                )
            )

    def gather_candidates(self, context):
        with tempfile.NamedTemporaryFile(
            mode='w', encoding=self.vars['encoding']
        ) as tf:
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
                        'action__path': info['file']
                    }

                    info['name'] = (
                        (info['name'][:33] + '..')
                        if len(info['name']) >= 33
                        else info['name']
                    )
                    info['file'] = Path(info['file']).name
                    fmt = '{name:<35} @{file:<25}'
                    if info['line']:
                        candidate['action__line'] = info['line']
                        fmt += ':{line} [{type}] {ref}'
                    else:
                        candidate['action__pattern'] = info['pattern']
                        m = re.search(r'\^\S*(.*)\$', info['pattern'])
                        if m:
                            info['pattern'] = '<-> ' + m.group(1).lstrip()
                        fmt += ' [{type}] {pattern}'
                    candidate['abbr'] = fmt.format(**info)

                    candidates.append(candidate)
        return candidates
