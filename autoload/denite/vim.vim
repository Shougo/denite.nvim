"=============================================================================
" FILE: vim.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

let s:denite_path = fnamemodify(expand('<sfile>'), ':p:h:h:h')
      \ . '/rplugin/python3'

function! denite#vim#_initialize() abort
  if v:version < 800 || !has('python3')
    call denite#util#print_error(
          \ 'denite.nvim does not work with this version.')
    call denite#util#print_error(
          \ 'It requires Vim 8.0+ with Python3 support("+python3").')
    return 1
  endif

  python3 << EOF
import sys
import vim
# Add sys.path
sys.path.insert(0, vim.eval('s:denite_path'))
import denite.util
import denite.ui.default
import denite.rplugin
# Define 'denite__uis' to store UI for individual buffers
denite__uis = {}
EOF
  let g:denite#_channel_id = getpid()
endfunction

function! denite#vim#_start(sources, context) abort
  python3 << EOF
def _temporary_scope():
    nvim = denite.rplugin.Neovim(vim)
    try:
        buffer_name = nvim.eval('a:context')['buffer_name']
        if nvim.eval('a:context')['buffer_name'] not in denite__uis:
            denite__uis[buffer_name] = denite.ui.default.Default(nvim)
        denite__uis[buffer_name].start(
            denite.rplugin.reform_bytes(nvim.eval('a:sources')),
            denite.rplugin.reform_bytes(nvim.eval('a:context')),
        )
    except Exception as e:
        import traceback
        for line in traceback.format_exc().splitlines():
            denite.util.error(nvim, line)
        denite.util.error(nvim, 'Please execute :messages command.')
_temporary_scope()
if _temporary_scope in dir():
    del _temporary_scope
EOF
  return []
endfunction

function! denite#vim#_do_action(context, action_name, targets) abort
  python3 << EOF
def _temporary_scope():
    nvim = denite.rplugin.Neovim(vim)
    try:
        buffer_name = nvim.eval('a:context')['buffer_name']
        if buffer_name not in denite__uis:
            denite__uis[buffer_name] = denite.ui.default.Default(nvim)
        denite__uis[buffer_name]._denite.do_action(
            denite.rplugin.reform_bytes(nvim.eval('a:context')),
            denite.rplugin.reform_bytes(nvim.eval('a:action_name')),
            denite.rplugin.reform_bytes(nvim.eval('a:targets')),
        )
    except Exception as e:
        import traceback
        for line in traceback.format_exc().splitlines():
            denite.util.error(nvim, line)
        denite.util.error(nvim, 'Please execute :messages command.')
_temporary_scope()
if _temporary_scope in dir():
    del _temporary_scope
EOF
  return []
endfunction
