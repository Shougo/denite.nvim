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
import denite.vim
import denite.rplugin
denite__rplugin = denite.rplugin.Rplugin(denite.vim.Neovim(vim))
EOF
  let g:denite#_channel_id = getpid()
endfunction

function! denite#vim#_start(args) abort
  python3 << EOF
def _temporary_scope():
    nvim = denite.vim.Neovim(vim)
    try:
        denite__rplugin.start(denite.vim.reform_bytes(
            nvim.eval('a:args')))
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

function! denite#vim#_do_action(args) abort
  python3 << EOF
def _temporary_scope():
    nvim = denite.vim.Neovim(vim)
    try:
        denite__rplugin.do_action(denite.vim.reform_bytes(
            nvim.eval('a:args')))
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
