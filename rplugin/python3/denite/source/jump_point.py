# ============================================================================
# FILE: jump_point.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
import os
from .base import Base


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'jump_point'
        self.kind = 'jump_list'

    def on_init(self, context):
        context['__line'] = self.vim.current.line

    def gather_candidates(self, context):
        result = parse_jump_line(context['__line'])
        self.debug(result)
        return [{'word': result[0],
                 'action__path': result[0],
                 'action__line': result[1],
                 'action__col': result[2],
                 }] if result and os.path.isfile(result[0]) else []


def parse_jump_line(line):
    m = re.search('^(.*):(\d+)(?::(\d+))?:(.*)$', line)
    if not m or not m.group(1) or not m.group(4):
        return []

    if re.search(':\d+$', m.group(1)):
        # Use column pattern
        m = re.search('^(.*):(\d+):(\d+):(.*)$', line)

    path = m.group(1)
    linenr = m.group(2)
    col = m.group(3)
    text = m.group(4)

    if not linenr:
        linenr = '1'
    if not col:
        col = '0'

    return [path, linenr, col, text]
