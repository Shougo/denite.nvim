# ============================================================================
# FILE: word.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pynvim import Nvim

from denite.base.kind import Base


class Kind(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'word'
        self.default_action = 'append'
