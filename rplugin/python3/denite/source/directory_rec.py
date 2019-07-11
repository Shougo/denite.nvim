# ============================================================================
# FILE: directory_rec.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         okamos <himinato.k at gmail.com>
# License: MIT license
# ============================================================================

from denite.source.file.rec import Source as Rec


class Source(Rec):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'directory_rec'
        self.kind = 'directory'

    def on_init(self, context):
        if not self.vars['command']:
            self.vars['command'] = [
                'find', '-L', ':directory',
                '-path', '*/.git/*', '-prune', '-o',
                '-type', 'l', '-print', '-o', '-type', 'd', '-print']

        super().on_init(context)

        if context['is_windows']:
            self.vars['command'] = []
            self.error_message(context,
                               'Windows environment is not supported.')

    def gather_candidates(self, context):
        candidates = [x for x in super().gather_candidates(context)
                      if x['action__path'] != context['__directory']]
        for candidate in candidates:
            candidate['abbr'] = candidate['word'] + '/'
        return candidates
