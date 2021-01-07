# ============================================================================
# FILE: matcher/hide_hidden_files.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
from re import match

from denite.base.filter import Base
from denite.util import Nvim, UserContext, Candidates


class Filter(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'matcher/hide_hidden_files'
        self.description = 'hide the hidden files'

    def filter(self, context: UserContext) -> Candidates:
        if '.' in context['input']:
            return list(context['candidates'])

        return [x for x in context['candidates']
                if not match(r'\.', Path(x['action__path']).name)]
