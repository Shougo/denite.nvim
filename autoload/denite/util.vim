"=============================================================================
" FILE: util.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#util#set_default(var, val, ...)  abort "{{{
  if !exists(a:var) || type({a:var}) != type(a:val)
    let alternate_var = get(a:000, 0, '')

    let {a:var} = exists(alternate_var) ?
          \ {alternate_var} : a:val
  endif
endfunction"}}}
function! denite#util#print_error(string) abort "{{{
  echohl Error | echomsg '[denite] ' . a:string | echohl None
endfunction"}}}
function! denite#util#print_warning(string) abort "{{{
  echohl WarningMsg | echomsg '[denite] ' . a:string | echohl None
endfunction"}}}

function! denite#util#convert2list(expr) abort "{{{
  return type(a:expr) ==# type([]) ? a:expr : [a:expr]
endfunction"}}}

function! denite#util#redir(cmd) abort "{{{
  let [save_verbose, save_verbosefile] = [&verbose, &verbosefile]
  set verbose=0 verbosefile=
  redir => res
  silent! execute a:cmd
  redir END
  let [&verbose, &verbosefile] = [save_verbose, save_verbosefile]
  return res
endfunction"}}}

function! denite#util#execute_path(command, path) abort "{{{
  execute a:command fnameescape(a:path)
endfunction"}}}

" vim: foldmethod=marker
