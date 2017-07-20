# ============================================================================
# FILE: tag.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import parse_tagline
from os.path import exists
import re


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.vim = vim
        self.name = 'tag'
        self.kind = 'file'

    def on_init(self, context):
        self.__tags = self.__get_tagfiles(context)

    def gather_candidates(self, context):
        candidates = []
        for f in self.__tags:
            with open(f, 'r', encoding=context['encoding'],
                      errors='replace') as ins:
                for line in ins:
                    if re.match('!', line) or not line:
                        continue
                    info = parse_tagline(line.rstrip(), f)
                    if not info:
                        continue
                    candidate = {
                        'word': info['name'],
                        'abbr': '{name} [{type}] {file} {ref}'.format(**info),
                        'action__path': info['file'],
                    }
                    if info['line']:
                        candidate['action__line'] = info['line']
                    else:
                        candidate['action__pattern'] = info['pattern']
                    candidates.append(candidate)

        return sorted(candidates, key=lambda value: value['word'])

    def __get_tagfiles(self, context):
        if (context['args'] and context['args'][0] == 'include' and
                self.vim.call('exists', '*neoinclude#include#get_tag_files')):
            tagfiles = self.vim.call('neoinclude#include#get_tag_files')
        else:
            tagfiles = self.vim.call('tagfiles')
        return [x for x in self.vim.call(
            'map', tagfiles, 'fnamemodify(v:val, ":p")') if exists(x)]
