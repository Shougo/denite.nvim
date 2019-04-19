# =============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# =============================================================================

from importlib.util import find_spec
from denite.rplugin import Rplugin

if find_spec('yarp'):
    import vim
elif find_spec('pynvim'):
    import pynvim
    vim = pynvim
else:
    import neovim
    vim = neovim

if hasattr(vim, 'plugin'):
    # Neovim only

    @vim.plugin
    class DeniteHandlers(object):
        def __init__(self, vim):
            self._rplugin = Rplugin(vim)

        @vim.function('_denite_init', sync=True)
        def init_channel(self, args):
            self._rplugin.init_channel(args)

        @vim.rpc_export('_denite_start', sync=True)
        def start(self, args):
            self._rplugin.start(args)

        @vim.rpc_export('_denite_do_action', sync=True)
        def take_action(self, args):
            return self._rplugin.take_action(args)

if find_spec('yarp'):

    global_denite = Rplugin(vim)

    def _denite_init():
        pass

    def _denite_start(args):
        global_denite.start(args)

    def _denite_do_action(args):
        return global_denite.take_action(args)
