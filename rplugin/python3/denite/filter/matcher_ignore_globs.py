# ============================================================================
# FILE: matcher_ignore_globs.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from os.path import isabs
from .base import Base
from fnmatch import fnmatch
from re import match


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher_ignore_globs'
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
        globs = []
        for glob in self.vars['ignore_globs']:
            if not isabs(glob):
                glob = '*/' + glob
            if match('\./', glob):
                glob = context['path'] + glob[1:]
            if glob[-1] == '/':
                glob += '*'
            globs.append(glob)
        return [x for x in context['candidates']
                if filter_globs(globs, x['action__path'])]


def filter_globs(globs, path):
    for glob in globs:
        if fnmatch(path, glob):
            return False
    return True
