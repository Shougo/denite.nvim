# ============================================================================
# FILE: openable.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from abc import abstractmethod
from copy import copy

from .base import Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'openable'
        self.default_action = 'open'

    @abstractmethod
    def action_open(self, context):
        pass

    def action_split(self, context):
        for target in context['targets']:
            new_context = copy(context)
            new_context['targets'] = [target]

            self.vim.command('split')
            self.action_open(new_context)

    def action_vsplit(self, context):
        for target in context['targets']:
            new_context = copy(context)
            new_context['targets'] = [target]

            self.vim.command('vsplit')
            self.action_open(new_context)

    def action_tabopen(self, context):
        hidden = self.vim.options['hidden']
        try:
            self.vim.options['hidden'] = False
            for target in context['targets']:
                new_context = copy(context)
                new_context['targets'] = [target]

                self.vim.command('tabnew')
                self.action_open(new_context)
        finally:
            self.vim.options['hidden'] = hidden

    def action_switch(self, context):
        self.__action_switch(context, self.action_open)

    def action_tabswitch(self, context):
        self.__action_switch(context, self.action_tabopen)

    def action_splitswitch(self, context):
        self.__action_switch(context, self.action_split)

    def action_vsplitswitch(self, context):
        self.__action_switch(context, self.action_vsplit)

    def __action_switch(self, context, fallback):
        for target in context['targets']:
            winid = self.__winid(target)
            if winid:
                self.vim.call('win_gotoid', winid)
            else:
                fallback(context)
