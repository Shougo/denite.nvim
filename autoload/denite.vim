"=============================================================================
" FILE: denite.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#initialize() abort "{{{
  return denite#init#_initialize()
endfunction"}}}
function! denite#start(sources, ...) abort "{{{
  let context = get(a:000, 0, {})
  call denite#initialize()
  call _denite_start(a:sources, context)
endfunction"}}}

" vim: foldmethod=marker
