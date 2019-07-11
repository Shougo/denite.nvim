# ============================================================================
# FILE: tag.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
from os.path import exists
from pathlib import Path

from denite.base.source import Base
from denite.util import parse_tagline

TAG_HIGHLIGHT_SYNTAX = [
    {'name': 'Type', 'link': 'Statement', 're': r'\[.\{-}\]'},
    {'name': 'File', 'link': 'Type', 're': r'@\w*\W\w*'},
    {'name': 'Pattern', 'link': 'Comment', 're': r'<->\s.*'},
]


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.vim = vim
        self.name = 'tag'
        self.kind = 'file'

    def on_init(self, context):
        self._tags = self._get_tagfiles(context)

    def highlight(self):
        for syn in TAG_HIGHLIGHT_SYNTAX:
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
        candidates = []
        for filename in self._tags:
            with open(filename, 'r',
                      encoding=context['encoding'],
                      errors='replace') as ins:
                for line in ins:
                    candidate = self._get_candidate(filename, line)
                    if candidate:
                        candidates.append(candidate)

        return sorted(candidates, key=lambda value: value['word'])

    def _get_candidate(self, filename, line):
        if re.match('!', line) or not line:
            return

        info = parse_tagline(line.rstrip(), filename)
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
        return candidate

    def _get_tagfiles(self, context):
        if (
            context['args']
            and context['args'][0] == 'include'
            and self.vim.call('exists', '*neoinclude#include#get_tag_files')
        ):
            tagfiles = self.vim.call('neoinclude#include#get_tag_files')
        else:
            tagfiles = self.vim.call('tagfiles')
        return [
            x
            for x in self.vim.call('map', tagfiles, 'fnamemodify(v:val, ":p")')
            if exists(x)
        ]
