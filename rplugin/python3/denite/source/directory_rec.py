# ============================================================================
# FILE: directory_rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         okamos <himinato.k at gmail.com>
# License: MIT license
# ============================================================================

import os

from denite.source.file.rec import Source as Rec
from denite.util import Nvim, UserContext, Candidates


class Source(Rec):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'directory_rec'
        self.kind = 'directory'

    def on_init(self, context: UserContext) -> None:
        if not self.vars['command']:
            if context['is_windows']:
                self.vars['command'] = [
                    'scantree.py', '--type', 'd', '--path', ':directory']
            else:
                self.vars['command'] = [
                    'find', '-L', ':directory',
                    '-path', '*/.git/*', '-prune', '-o',
                    '-type', 'l', '-print', '-o', '-type', 'd', '-print']

        super().on_init(context)

    def gather_candidates(self, context: UserContext) -> Candidates:
        candidates = [x for x in super().gather_candidates(context)
                      if x['action__path'] != context['__directory']]
        for candidate in candidates:
            candidate['abbr'] = candidate['word'] + os.sep
        return candidates
