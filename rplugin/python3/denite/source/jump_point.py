# ============================================================================
# FILE: jump_point.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import parse_jump_line
import os


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'jump_point'
        self.kind = 'jump_list'

    def on_init(self, context):
        context['__line'] = self.vim.current.line

    def gather_candidates(self, context):
        result = parse_jump_line(
            self.vim.call('getcwd'), context['__line'])
        return [{
            'word': '{0}: {1}{2}: {3}'.format(
                result[0], result[1],
                (': ' + result[2] if result[2] != '0' else ''),
                result[3]),
            'action__path': result[0],
            'action__line': result[1],
            'action__col': result[2],
        }] if result and os.path.isfile(result[0]) else []
