# =============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# =============================================================================

from importlib import find_loader


if not find_loader('vim'):
    import neovim
    from denite.ui.default import Default

    @neovim.plugin
    class DeniteHandlers(object):
        def __init__(self, vim):
            self.__vim = vim

        @neovim.function('_denite_init', sync=True)
        def init_python(self, args):
            self.__ui = Default(self.__vim)
            self.__vim.vars['denite#_channel_id'] = self.__vim.channel_id
            return

        @neovim.function('_denite_start', sync=True)
        def start(self, args):
            self.__ui = Default(self.__vim)
            return self.__ui.start(args[0], args[1])
