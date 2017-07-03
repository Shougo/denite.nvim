"=============================================================================
" FILE: context.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#context#get(...) abort
  let key = a:0 ? a:1 : v:null
  let bufname = a:0 > 1 ? a:2 : 'default'
  if has('nvim')
    return _denite_get_context(key, bufname)
  else
    call denite#initialize()
    return denite#vim#_get_context(key, bufname)
  endif
endfunction

function! denite#context#set(key, value, ...) abort
  let bufname = a:0 ? a:1 : 'default'
  if has('nvim')
    return _denite_set_context(a:key, a:value, bufname)
  else
    call denite#initialize()
    return denite#vim#_set_context(a:key, a:value, bufname)
  endif
endfunction
