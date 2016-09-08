# ============================================================================
# FILE: matcher_project_files.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import path2project


class Filter(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'matcher_project_files'
        self.description = 'project files matcher'

    def filter(self, context):
        path = context['path'] if context[
            'path'] != '' else self.vim.call('getcwd')
        project = path2project(path) + '/'

        return [x for x in context['candidates']
                if 'action__path' not in x or
                x['action__path'].find(project) == 0]
