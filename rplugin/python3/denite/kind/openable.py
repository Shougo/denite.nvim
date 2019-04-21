# ============================================================================
# FILE: openable.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from abc import abstractmethod
from copy import copy

from denite.base.kind import Base


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'openable'
        self.default_action = 'open'

    @abstractmethod
    def action_open(self, context):
        pass

    def action_split(self, context):
        if self._is_current_buffer_empty():
            self.action_open(context)
            return

        for target in context['targets']:
            new_context = copy(context)
            new_context['targets'] = [target]

            self.vim.command('split')
            self.action_open(new_context)

    def action_vsplit(self, context):
        if self._is_current_buffer_empty():
            self.action_open(context)
            return

        for target in context['targets']:
            new_context = copy(context)
            new_context['targets'] = [target]

            self.vim.command('vsplit')
            self.action_open(new_context)

    def action_tabopen(self, context):
        if self._is_current_buffer_empty():
            self.action_open(context)
            return

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
        self._action_switch(context, self.action_open)

    def action_tabswitch(self, context):
        self._action_switch(context, self.action_tabopen)

    def action_splitswitch(self, context):
        self._action_switch(context, self.action_split)

    def action_vsplitswitch(self, context):
        self._action_switch(context, self.action_vsplit)

    def _action_switch(self, context, fallback):
        for target in context['targets']:
            winid = self._winid(target)
            if winid:
                self.vim.call('win_gotoid', winid)
                if callable(self._jump):
                    self._jump(context, target)
            else:
                fallback(context)

    def _is_current_buffer_empty(self):
        buffer = self.vim.current.buffer
        return buffer.name == '' and len(buffer) == 1 and buffer[0] == ''
