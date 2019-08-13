# =============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# =============================================================================

import typing

from importlib.util import find_spec
from denite.rplugin import Rplugin
from denite.util import Nvim

if find_spec('yarp'):
    import vim
elif find_spec('pynvim'):
    import pynvim
    vim = pynvim
else:
    import neovim
    vim = neovim

Args = typing.List[typing.Any]

if hasattr(vim, 'plugin'):
    # Neovim only

    @vim.plugin
    class DeniteHandlers(object):
        def __init__(self, vim: Nvim) -> None:
            self._rplugin = Rplugin(vim)

        @vim.function('_denite_init', sync=True)  # type: ignore
        def init_channel(self, args: Args) -> None:
            self._rplugin.init_channel(args)

        @vim.rpc_export('_denite_start', sync=True)  # type: ignore
        def start(self, args: Args) -> None:
            self._rplugin.start(args)

        @vim.rpc_export('_denite_do_action', sync=True)  # type: ignore
        def do_action(self, args: Args) -> typing.Any:
            return self._rplugin.do_action(args)

        @vim.rpc_export('_denite_do_map', sync=True)  # type: ignore
        def do_map(self, args: Args) -> typing.Any:
            return self._rplugin.do_map(args)

        @vim.rpc_export('_denite_do_async_map', sync=False)  # type: ignore
        def do_async_map(self, args: Args) -> typing.Any:
            return self._rplugin.do_map(args)

if find_spec('yarp'):

    global_denite = Rplugin(vim)

    def _denite_init() -> None:
        pass

    def _denite_start(args: Args) -> None:
        global_denite.start(args)

    def _denite_do_action(args: Args) -> typing.Any:
        return global_denite.do_action(args)

    def _denite_do_map(args: Args) -> typing.Any:
        return global_denite.do_map(args)

    def _denite_do_async_map(args: Args) -> typing.Any:
        return global_denite.do_map(args)
