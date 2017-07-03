# =============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# =============================================================================

import traceback
from importlib import find_loader


if not find_loader('vim'):
    import neovim
    from denite.ui.default import Default
    _uis = {}

    @neovim.plugin
    class DeniteHandlers(object):
        def __init__(self, vim):
            self._vim = vim

        @neovim.function('_denite_init', sync=True)
        def init_python(self, args):
            _uis.clear()
            self._vim.vars['denite#_channel_id'] = self._vim.channel_id
            return

        @neovim.function('_denite_start', sync=True)
        def start(self, args):
            from denite.util import error
            try:
                buffer_name = args[1]['buffer_name']
                if buffer_name not in _uis:
                    _uis[buffer_name] = Default(self._vim)
                return _uis[buffer_name].start(args[0], args[1])
            except Exception:
                for line in traceback.format_exc().splitlines():
                    error(self._vim, line)
                error(self._vim, 'Please execute :messages command.')

        @neovim.function('_denite_get_context', sync=True)
        def get_context(self, args):
            key, bufname = args
            if not _uis:
                return
            if key:
                context = _uis[bufname]._context
                return context[key]
            else:
                # Return list of keys of any UI
                return sorted(next(iter(_uis.values()))._context)

        @neovim.function('_denite_set_context', sync=True)
        def set_context(self, args):
            key, value, bufname = args
            if not _uis:
                return
            context = _uis[bufname]._context
            context[key] = value
