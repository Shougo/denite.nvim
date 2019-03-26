
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

    def on_init(self, context):
        args = dict(enumerate(context['args']))
        self.arg = args.get(0, self.vim.funcs.expand("<cword>"))

    def gather_candidates(self, context):
        candidates = []
        for word in self.vim.funcs.spellsuggest(self.arg):
            candidates += [{
                'word' : word
            }]
        return candidates
