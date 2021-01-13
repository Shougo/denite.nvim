# ============================================================================
# FILE: converter/expand_input.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.filter import Base
from denite.util import Nvim, UserContext, Candidates, expand


class Filter(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'converter/expand_input'
        self.description = 'convert expand input'

    def filter(self, context: UserContext) -> Candidates:
        context['input'] = expand(context['input'])
        return list(context['candidates'])
