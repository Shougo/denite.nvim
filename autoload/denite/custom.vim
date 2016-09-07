"=============================================================================
" FILE: custom.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#custom#get() abort "{{{
  if !exists('s:custom')
    let s:custom = {}
    let s:custom.source = {}
    let s:custom.source._ = {}
    let s:custom.map = {}
    let s:custom.map._ = {}
  endif

  return s:custom
endfunction"}}}

function! denite#custom#source(source_name, option_name, value) abort "{{{
  let custom = denite#custom#get()

  for key in split(a:source_name, '\s*,\s*')
    if !has_key(custom.source, key)
      let custom.source[key] = {}
    endif
    let custom_source = custom.source[key]
    let custom_source[a:option_name] = a:value
  endfor
endfunction"}}}

function! denite#custom#map(mode, key, mapping, ...) abort "{{{
  let custom = denite#custom#get()
  let options = get(a:000, 0, {})

  for key in split(a:mode, '\s*,\s*')
    if !has_key(custom.map, key)
      let custom.map[key] = {}
    endif
    let custom_map = custom.map[key]
    let custom_map[a:key] = a:mapping
  endfor
endfunction"}}}

" vim: foldmethod=marker
