"=============================================================================
" FILE: custom.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#custom#_get() abort
  if !exists('s:custom')
    call denite#custom#_init()
  endif

  return s:custom
endfunction

function! denite#custom#_init() abort
  let s:custom = {}
  let s:custom.source = {}
  let s:custom.source._ = {}
  let s:custom.map = {}
  let s:custom.map._ = []
  let s:custom.alias_source = {}
  let s:custom.alias_filter = {}
  let s:custom.option = {}
  let s:custom.filter = {}
  let s:custom.action = {}
endfunction

function! denite#custom#source(source_name, option_name, value) abort
  if index(['matchers', 'sorters', 'converters',
        \   'vars', 'args', 'max_candidates'],
        \ a:option_name) < 0
    call denite#util#print_error('Invalid option_name: ' . a:option_name)
    return
  endif

  let custom = denite#custom#_get().source

  for key in denite#util#split(a:source_name)
    if !has_key(custom, key)
      let custom[key] = {}
    endif
    let custom[key][a:option_name] = a:value
  endfor
endfunction

function! denite#custom#filter(filter_name, var_name, value) abort
  let custom = denite#custom#_get().filter

  for key in denite#util#split(a:filter_name)
    if !has_key(custom, key)
      let custom[key] = {}
    endif
    let custom[key][a:var_name] = a:value
  endfor
endfunction

function! denite#custom#var(source_name, var_name, value) abort
  let custom = denite#custom#_get().source

  for key in denite#util#split(a:source_name)
    if !has_key(custom, key)
      let custom[key] = {}
    endif
    if !has_key(custom[key], 'vars')
      let custom[key].vars = {}
    endif
    let custom[key].vars[a:var_name] = a:value
  endfor
endfunction

function! denite#custom#map(mode, key, mapping, ...) abort
  let custom = denite#custom#_get().map
  let params = get(a:000, 0, '')

  for mode in denite#util#split(a:mode)
    let custom[mode] = get(custom, mode, [])
    call add(custom[mode], [a:key, a:mapping, params])
  endfor
endfunction

function! denite#custom#alias(type, name, base) abort
  if a:type ==# 'source'
    let custom = denite#custom#_get().alias_source
  elseif a:type ==# 'filter'
    let custom = denite#custom#_get().alias_filter
  else
    return denite#util#print_error('Invalid alias type: ' . a:type)
  endif

  if !has_key(custom, a:base)
    let custom[a:base] = []
  endif
  let custom[a:base] = uniq(sort(add(custom[a:base], a:name)))
endfunction

function! denite#custom#option(buffer_name, name_or_dict, ...) abort
  let custom = denite#custom#_get().option

  for key in denite#util#split(a:buffer_name)
    if !has_key(custom, key)
      let custom[key] = {}
    endif

    call s:set_custom(custom[key], a:name_or_dict, get(a:000, 0, ''))
  endfor
endfunction

function! denite#custom#action(kind, name, func, ...) abort
  let custom = denite#custom#_get().action

  for key in denite#util#split(a:kind)
    if !has_key(custom, key)
      let custom[key] = {}
    endif
    let custom[key][a:name] = [a:func, a:0 ? a:1 : {}]
  endfor
endfunction
function! denite#custom#_call_action(kind, name, context) abort
  let custom = denite#custom#_get().action

  for key in denite#util#split(a:kind)
    if has_key(custom, key) && has_key(custom[key], a:name)
      call call(custom[key][a:name][0], [a:context])
    endif
  endfor
endfunction

function! s:set_custom(dest, name_or_dict, value) abort
  if type(a:name_or_dict) == v:t_dict
    call extend(a:dest, a:name_or_dict)
  else
    let a:dest[a:name_or_dict] = a:value
  endif
endfunction
