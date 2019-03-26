# ============================================================================
# FILE: spell.py
# AUTHOR: Milan Svoboda <milan.svoboda@centrum.cz>
# License: MIT license
# ============================================================================

from denite.base.source import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.vim = vim
        self.name = 'spell'
        self.default_action = 'replace'

        self._arg = ''

    def on_init(self, context):
        args = dict(enumerate(context['args']))
        context['__arg'] = args.get(0, self.vim.call('expand', '<cword>'))

    def gather_candidates(self, context):
        return [{'word': x} for x in
                self.vim.call('spellsuggest', context['__arg'])]
