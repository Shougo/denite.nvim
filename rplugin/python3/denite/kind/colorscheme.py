from ..kind.command import Kind as Command

class Kind(Command):
    def __init__(self, vim):
        super().__init__(vim)
        self.vim = vim
        self.name = 'colorscheme'

    def action_preview(self, context):
        target = context['targets'][0]
        self.vim.command('silent colorscheme {}'.format(target['word']))

