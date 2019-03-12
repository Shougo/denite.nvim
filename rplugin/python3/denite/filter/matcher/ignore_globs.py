# ============================================================================
# FILE: matcher/ignore_globs.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from os.path import isabs, sep
from fnmatch import translate
from re import search

from denite.base.filter import Base


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher/ignore_globs'
        self.description = 'ignore the globs matched files'
        self.vars = {
            'ignore_globs': [
               '*~', '*.o', '*.exe', '*.bak',
               '.DS_Store', '*.pyc', '*.sw[po]', '*.class',
               '.hg/', '.git/', '.bzr/', '.svn/',
               'tags', 'tags-*'
            ]
        }

    def filter(self, context):
        # Convert globs
        patterns = []
        for glob in self.vars['ignore_globs']:
            if not isabs(glob):
                glob = '*' + sep + glob
            if glob[:2] == '.' + sep:
                glob = context['path'] + glob[1:]
            if glob[-1] == sep:
                glob += '*'
            patterns.append(translate(glob))
        pattern = '|'.join(patterns)
        max_width = int(context['max_candidate_width'])
        return [x for x in context['candidates']
                if 'action__path' not in x or
                not search(pattern, x['action__path'][:max_width])]
