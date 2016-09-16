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
  let context.custom = denite#custom#get()

  call denite#initialize()
  if has('nvim')
    return _denite_start(a:sources, context)
  else
    return denite#vim#_start(a:sources, context)
  endif
endfunction"}}}

" vim: foldmethod=marker
