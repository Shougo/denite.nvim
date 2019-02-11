# ============================================================================
# FILE: rplugin.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.ui.default import Default
from denite.context import Context


class Rplugin:

    def __init__(self, vim):
        self._vim = vim
        self._uis = {}
        self._context = Context(self._vim)

    def init_channel(self, args):
        self._vim.vars['denite#_channel_id'] = self._vim.channel_id

    def start(self, args):
        try:
            context = self._context.get(args[1])
            ui = self.get_ui(context['buffer_name'])
            return ui.start(args[0], context)
        except Exception:
            import traceback
            import denite.util
            for line in traceback.format_exc().splitlines():
                denite.util.error(self._vim, line)
            denite.util.error(self._vim,
                              'Please execute :messages command.')

    def take_action(self, args):
        try:
            ui = self.get_ui(args[0]['buffer_name'])
            return ui._denite.do_action(args[0], args[1], args[2])
        except Exception:
            import traceback
            import denite.util
            for line in traceback.format_exc().splitlines():
                denite.util.error(self._vim, line)
            denite.util.error(self._vim,
                              'Please execute :messages command.')

    def get_ui(self, buffer_name):
        if buffer_name not in self._uis:
            self._uis[buffer_name] = Default(self._vim)
        return self._uis[buffer_name]
