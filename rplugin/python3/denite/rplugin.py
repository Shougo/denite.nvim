# ============================================================================
# FILE: rplugin.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pynvim import Nvim
import typing

from denite.context import Context
from denite.parent import SyncParent

Args = typing.List[typing.Any]


class Rplugin:

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim
        self._uis: typing.Dict[str, typing.Any] = {}

    def init_channel(self, args: Args) -> None:
        self._vim.vars['denite#_channel_id'] = self._vim.channel_id

    def start(self, args: Args) -> typing.Any:
        try:
            context = Context(self._vim).get(args[1])
            ui = self.get_ui(context['buffer_name'])
            return ui.start(args[0], context)
        except NameError as ex:
            import denite.util
            denite.util.error(self._vim, str(ex))
        except Exception:
            import traceback
            import denite.util
            for line in traceback.format_exc().splitlines():
                denite.util.error(self._vim, line)
            denite.util.error(self._vim,
                              'Please execute :messages command.')

    def do_action(self, args: Args) -> typing.Any:
        try:
            ui = self.get_ui(args[0]['buffer_name'])
            ui._cursor = self._vim.call('line', '.')
            return ui._denite.do_action(args[0], args[1], args[2])
        except Exception:
            import traceback
            import denite.util
            for line in traceback.format_exc().splitlines():
                denite.util.error(self._vim, line)
            denite.util.error(self._vim,
                              'Please execute :messages command.')

    def do_targets(self, args: Args) -> typing.Any:
        try:
            dnt = SyncParent(self._vim)
            context = Context(self._vim).get(args[0])
            dnt.start(context)
            dnt.on_init(context)
            return dnt.do_action(context, args[1], args[2])
        except Exception:
            import traceback
            import denite.util
            for line in traceback.format_exc().splitlines():
                denite.util.error(self._vim, line)
            denite.util.error(self._vim,
                              'Please execute :messages command.')

    def do_map(self, args: Args) -> typing.Any:
        from denite.ui.map import do_map
        bufnr = args[0]
        if not self._vim.call('bufexists', bufnr):
            return
        bufvars = self._vim.buffers[bufnr].vars
        if 'denite' not in bufvars:
            return

        try:
            buffer_name = bufvars['denite']['buffer_name']
            ui = self.get_ui(buffer_name)
            ui._cursor = self._vim.call('line', '.')
            ui._context['next_actions'] = []

            ret = do_map(ui, args[1], args[2])

            if args[1] == 'quit' and buffer_name[-1] == '@':
                # Temporary buffer quit
                # Resume the previous buffer
                self.resume(buffer_name[:-1])

            if ui._context['next_actions']:
                actions = ui._context['next_actions']
                ui._context['next_actions'] = []

                # Do actions
                for action in actions:
                    ui = self.get_ui(action['buffer_name'])
                    self.resume(action['buffer_name'])

                    ui.do_action(
                        action['name'], '', True, action['targets']
                    )

            return ret
        except Exception:
            import traceback
            import denite.util
            for line in traceback.format_exc().splitlines():
                denite.util.error(self._vim, line)
            denite.util.error(self._vim,
                              'Please execute :messages command.')

    def get_ui(self, buffer_name: str) -> typing.Any:
        from denite.ui.default import Default
        if buffer_name not in self._uis:
            self._uis[buffer_name] = Default(self._vim)
        return self._uis[buffer_name]

    def resume(self, buffer_name: str) -> None:
        ui = self.get_ui(buffer_name)
        ui._context.update({
            'buffer_name': buffer_name,
            'resume': True
        })
        ui.start([], ui._context)
