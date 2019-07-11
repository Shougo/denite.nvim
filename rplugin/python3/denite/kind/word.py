# ============================================================================
# FILE: word.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.base.kind import Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'word'
        self.default_action = 'append'
