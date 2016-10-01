# ============================================================================
# FILE: menu.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         okamos <himinato.k at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from os import listdir


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'buffer_dir'
        self.kind = 'open_dir_or_jump_list'

    def on_init(self, context):
        directory = context['args'][0] if len(
            context['args']) > 0 else self.vim.call('expand', '%:p:h')
        context['__directory'] = directory

    def gather_candidates(self, context):
        files = []

        for file in ['..'] + listdir(context['__directory']):
            d = dict({
                'word': file,
                'action__path': context['__directory'] + '/' + file
            })
            files.append(d)

        return sorted(files, key=lambda v: v['word'])
