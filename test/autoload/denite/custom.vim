" set verbose=1

let s:suite = themis#suite('custom')
let s:assert = themis#helper('assert')

function! s:suite.before_each() abort
  call denite#custom#_init()
endfunction

function! s:suite.custom_source() abort
  let custom = denite#custom#_get().source
  call denite#custom#source(
        \ 'file_mru', 'matchers', ['matcher_fuzzy', 'matcher_project_files'])
  call denite#custom#source(
        \ 'file/rec', 'matchers', ['matcher_cpsm'])
  call s:assert.equals(custom.file_mru.matchers,
        \ ['matcher_fuzzy', 'matcher_project_files'])
  call s:assert.equals(custom['file/rec'].matchers,
        \ ['matcher_cpsm'])
endfunction

function! s:suite.custom_filter() abort
  let custom = denite#custom#_get().filter

  call denite#custom#filter('matcher_ignore_globs', 'ignore_globs',
        \ [])
  call s:assert.equals(custom.matcher_ignore_globs.ignore_globs,
        \ [])
endfunction

function! s:suite.custom_var() abort
  let custom = denite#custom#_get().source

  call denite#custom#var('file/rec', 'command',
        \ ['rg', '--files'])
  call s:assert.equals(custom['file/rec'].vars.command,
        \ ['rg', '--files'])
endfunction

function! s:suite.custom_map() abort
  let custom = denite#custom#_get().map

  call denite#custom#map('_', '<C-j>', '<denite:move_to_next_line>')
  call denite#custom#map('_', '<C-k>', '<denite:move_to_previous_line>')
  call s:assert.equals(custom._, [
        \ ['<C-j>', '<denite:move_to_next_line>', ''],
        \ ['<C-k>', '<denite:move_to_previous_line>', ''],
        \])
endfunction

function! s:suite.custom_alias() abort
  let custom = denite#custom#_get().alias_source

  call denite#custom#alias('source', 'file/rec/git', 'file/rec')
  call s:assert.equals(custom['file/rec'], ['file/rec/git'])

  let custom = denite#custom#_get().alias_filter
  call denite#custom#alias('filter', 'matcher_bar', 'matcher_foo')
  call s:assert.equals(custom['matcher_foo'], ['matcher_bar'])
endfunction

function! s:suite.custom_option() abort
  let custom = denite#custom#_get().option

  call denite#custom#option('default', 'prompt', '>')
  call s:assert.equals(custom.default.prompt, '>')
endfunction
