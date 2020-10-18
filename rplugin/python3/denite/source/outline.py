# ============================================================================
# FILE: outline.py
# AUTHOR: Yasumasa Tamura (tamura.yasumasa _at_ gmail.com)
# License: MIT license
# ============================================================================

import re
import tempfile
import typing
from pathlib import Path
from subprocess import CalledProcessError, check_output, run, PIPE
from json import loads

from denite.base.source import Base
from denite.util import parse_tagline, Nvim, UserContext, Candidates

OUTLINE_HIGHLIGHT_SYNTAX = [
    {'name': 'Type', 'link': 'Statement', 're': r'\[.\{-}\]'},
    {'name': 'File', 'link': 'Type', 're': r'\d\+ *@\w*\W\w*'},
    {'name': 'Pattern', 'link': 'Comment', 're': r'<->\s.*'},
]


class Source(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'outline'
        self.kind = 'file'
        self.vars = {
            'force_filetype': True,
            'language_map': {'cpp': 'c++', 'zsh': 'sh'},
            'output': 'legacy',
            'command': ['ctags'],
            'options': [],
            'file_opt': '-o',
            'ignore_types': [],
            'encoding': 'utf-8',
        }

    def on_init(self, context: UserContext) -> None:
        cur_buffer = self.vim.current.buffer
        context['__path'] = (
            context['args'][0]
            if len(context['args']) > 0
            else cur_buffer.name
        )
        if len(context['args']) <= 0 and not self.vim.funcs.filereadable(
                cur_buffer.name):
            context['__nofile'] = True
            context['__bufnr'] = int(cur_buffer.number)
            self.default_action = 'switch'
        if self.vars['force_filetype']:
            context['__language'] = cur_buffer.options['filetype']
            ctags_filetype = self.vars['language_map'].get(
                context['__language'], None)
            if ctags_filetype:
                context['__language'] = ctags_filetype

    def highlight(self) -> None:
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

    def gather_candidates(self, context: UserContext) -> Candidates:
        if self.vars['output'] == 'legacy':
            return self.gather_candidates_legacy(context)
        elif self.vars['output'] == 'json':
            return self.gather_candidates_universal(context)
        else:
            return []

    def gather_candidates_universal(self, context: UserContext) -> Candidates:
        args: typing.List[str] = []
        args += self.vars['command']
        args += self.vars['options']
        if self.vars['force_filetype'] and '__language' in context:
            args.append('--language-force={}'.format(context['__language']))
        args += ['--output-format=json', '-f', '-']
        if context.get('__nofile', False):
            tempfile = self.vim.funcs.tempname()
            with open(tempfile, "w") as f:
                f.writelines(
                    map(lambda x: x + '\n',
                        self.vim.buffers[context['__bufnr']][:]))
            args += [tempfile]
        else:
            args += [context['__path']]
        self.print_message(context, ' '.join(args))

        try:
            p = run(args, check=True, stdout=PIPE, stderr=PIPE)
            outputs = p.stdout.decode(self.vars['encoding']).splitlines()
        except CalledProcessError as e:
            err_msg = e.stderr.decode(self.vars['encoding']).splitlines()
            self.error_message(context, err_msg)
            return []

        candidates = []
        for entry in outputs:
            info = loads(entry)

            candidate = {
                'word':
                info['name'],
                'action__path':
                info['path']
                if not context.get('__nofile') else context['__path'],
            }
            candidates.append(candidate)

            fmt = '{name:<35.35} '
            if 'line' in info:
                candidate['action__line'] = info['line']
                fmt += '{line:<6}'
            if 'scope' in info:
                fmt += '@{scope:<25.25}'
            else:
                info['file'] = Path(info['path']).name
                fmt += '@{file:<25}'
            if 'kind' in info:
                info['kind'] = info['kind'][0]
                fmt += ' [{kind}]'
            if 'pattern' in info:
                if 'line' not in info:
                    candidate['action__pattern'] = info['pattern']
                info['pattern'] = info['pattern'][2:-2].lstrip(' \t\v')
                info['pattern'] = '<-> ' + info['pattern']
                fmt += ' {pattern}'
            candidate['abbr'] = fmt.format(**info)

        return candidates

    def gather_candidates_legacy(self, context: UserContext) -> Candidates:
        with tempfile.NamedTemporaryFile(
            mode='w', encoding=self.vars['encoding']
        ) as tf:
            args: typing.List[str] = []
            args += self.vars['command']
            args += self.vars['options']
            args += [self.vars['file_opt'], tf.name]
            args += [context['__path']]
            self.print_message(context, ' '.join(args))
            # Close this file before giving to ctags
            # Otherwise this will error on Windows
            tf.close()

            try:
                check_output(args).decode(self.vars['encoding'], 'replace')
            except CalledProcessError:
                return []

            ignore_types = self.vars['ignore_types']

            candidates = []
            with open(tf.name, encoding=self.vars['encoding'],
                      errors='replace') as f:
                for line in f:
                    if re.match('!', line) or not line:
                        continue
                    info = parse_tagline(line.rstrip(), tf.name)
                    if info['type'] in ignore_types:
                        continue
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
