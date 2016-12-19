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
# Define 'denite__uis' to store UI for individual buffers
denite__uis = {}
EOF
  let g:denite#_channel_id = getpid()
endfunction

function! denite#vim#_start(sources, context) abort
  python3 << EOF
def _temporary_scope():
    import traceback
    import vim
    from denite.util import error
    from denite.rplugin import Neovim, reform_bytes
    nvim = Neovim(vim)
    try:
        from denite.ui.default import Default
        buffer_name = nvim.eval('a:context')['buffer_name']
        if buffer_name not in denite__uis:
            denite__uis[buffer_name] = Default(nvim)
        denite__uis[buffer_name].start(
            reform_bytes(nvim.bindeval('a:sources')),
            reform_bytes(nvim.bindeval('a:context')),
        )
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            error(nvim, line)
        error(nvim, 'Please execute :messages command.')
_temporary_scope()
if _temporary_scope in dir():
    del _temporary_scope
EOF
  return []
endfunction
