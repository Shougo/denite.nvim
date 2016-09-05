"=============================================================================
" FILE: custom.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#custom#get() abort "{{{
  if !exists('s:custom')
    let s:custom = {}
    let s:custom._ = {}
  endif

  return s:custom
endfunction"}}}

function! denite#custom#get_source_var(source_name) abort "{{{
  let custom = denite#custom#get()

  if !has_key(custom, a:source_name)
    let custom[a:source_name] = {}
  endif

  return custom[a:source_name]
endfunction"}}}

function! denite#custom#source(source_name, option_name, value) abort "{{{
  for key in split(a:source_name, '\s*,\s*')
    let custom_source = denite#custom#get_source_var(key)
    let custom_source[a:option_name] = a:value
  endfor
endfunction"}}}

" vim: foldmethod=marker
