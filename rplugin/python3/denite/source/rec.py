# ============================================================================
# FILE: rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
import subprocess


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'rec'

    def gather_candidates(self, context):
        args = ['find', '-L', '.', '-path', '*/.git/*', '-prune', '-o',
                '-type', 'l', '-print', '-o', '-type', 'f', '-print']
        return [{'word': x, 'action__path': x}
                for x in subprocess.check_output(args).decode(
                        'utf-8').split('\n')]
