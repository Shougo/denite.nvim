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
    let s:custom.alias_source = {}
    let s:custom.alias_filter = {}
    let s:custom.option = {}
  endif

  return s:custom
endfunction"}}}

function! denite#custom#source(source_name, option_name, value) abort "{{{
  let custom = denite#custom#get().source

  for key in denite#util#split(a:source_name)
    if !has_key(custom, key)
      let custom[key] = {}
    endif
    let custom[key][a:option_name] = a:value
  endfor
endfunction"}}}

function! denite#custom#var(source_name, var_name, value) abort "{{{
  let custom = denite#custom#get().source

  for key in denite#util#split(a:source_name)
    if !has_key(custom, key)
      let custom[key] = {}
    endif
    if !has_key(custom[key], 'vars')
      let custom[key]['vars'] = {}
    endif
    let custom[key]['vars'][a:var_name] = a:value
  endfor
endfunction"}}}

function! denite#custom#map(mode, key, mapping, ...) abort "{{{
  let custom = denite#custom#get().map
  " let options = get(a:000, 0, {})

  for key in denite#util#split(a:mode)
    if !has_key(custom, key)
      let custom[key] = {}
    endif
    let custom[key][denite#util#char2key(a:key)] = a:mapping
  endfor
endfunction"}}}

function! denite#custom#alias(type, name, base) abort "{{{
  if a:type ==# 'source'
    let custom = denite#custom#get().alias_source
  elseif a:type ==# 'filter'
    let custom = denite#custom#get().alias_filter
  else
    return denite#util#print_error('Invalid alias type: ' . a:type)
  endif

  if !has_key(custom, a:base)
    let custom[a:base] = []
  endif
  let custom[a:base] = uniq(sort(add(custom[a:base], a:name)))
endfunction"}}}

function! denite#custom#option(buffer_name, option_name, value) abort "{{{
  let custom = denite#custom#get().option

  for key in denite#util#split(a:buffer_name)
    if !has_key(custom, key)
      let custom[key] = {}
    endif
    let custom[key][a:option_name] = a:value
  endfor
endfunction"}}}

" vim: foldmethod=marker
