"=============================================================================
" FILE: vim.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

let s:denite_path = fnamemodify(expand('<sfile>'), ':p:h:h:h')
      \ . '/rplugin/python3'

function! denite#vim#_initialize() abort "{{{
  if v:version < 800 || !has('python3')
    call denite#util#print_error(
          \ 'denite.nvim does not work with this version.')
    call denite#util#print_error(
          \ 'It requires Vim 8.0+ with Python3 support("+python3").')
    return 1
  endif

  python3 << EOF
import vim
# Add sys.path
sys.path.insert(0, vim.eval('s:denite_path'))

import denite.ui.default
denite_ui = denite.ui.default.Default(vim)
EOF

  call denite#init#_variables()
endfunction"}}}

function! denite#vim#_start(sources, context) abort "{{{
  python3 << EOF
import vim
denite_ui.start(vim.eval('a:sources'), vim.eval('a:context'))
EOF
  return []
endfunction"}}}

" vim: foldmethod=marker
