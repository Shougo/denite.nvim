"=============================================================================
" FILE: helper.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#helper#complete(arglead, cmdline, cursorpos) abort "{{{
  let _ = []

  if a:arglead !~ ':'
    " Option names completion.
    let _ += map(copy(denite#helper#options()), "'-' . v:val")

    " Source name completion.
    let _ += map(globpath(&runtimepath,
          \ 'rplugin/python3/denite/source/*.py', 1, 1),
          \ "fnamemodify(v:val, ':t:r')")
  endif

  return uniq(sort(filter(_, 'stridx(v:val, a:arglead) == 0')))
endfunction"}}}

function! denite#helper#call_denite(command, args, line1, line2) abort "{{{
  let [args, context] = s:parse_options_args(a:args)

  let context.firstline = a:line1
  let context.lastline = a:line2
  let context.bufnr = bufnr('%')
  if a:command ==# 'DeniteCursorWord'
    let context.input = expand('<cword>')
  elseif a:command ==# 'DeniteBufferDir'
    let context.path = fnamemodify(bufname('%'), ':p:h')
  endif

  call denite#start(args, context)
endfunction"}}}

function! denite#helper#options() abort "{{{
  return map(keys(denite#init#_user_options()), "tr(v:val, '_', '-')")
endfunction"}}}

function! s:parse_options(cmdline) abort "{{{
  let args = []
  let options = {}

  " Eval
  let cmdline = (a:cmdline =~ '\\\@<!`.*\\\@<!`') ?
        \ s:eval_cmdline(a:cmdline) : a:cmdline

  for arg in split(cmdline, '\%(\\\@<!\s\)\+')
    let arg = substitute(arg, '\\\( \)', '\1', 'g')
    let arg_key = substitute(arg, '=\zs.*$', '', '')

    let name = substitute(tr(arg_key, '-', '_'), '=$', '', '')[1:]
    let value = (arg_key =~ '=$') ? arg[len(arg_key) :] : 1

    if index(keys(denite#init#_user_options()), name) >= 0
      let options[name] = value
    else
      call add(args, arg)
    endif
  endfor

  return [args, options]
endfunction"}}}
function! s:parse_options_args(cmdline) abort "{{{
  let _ = []
  let [args, options] = s:parse_options(a:cmdline)
  for arg in args
    " Add source name.
    let source_name = matchstr(arg, '^[^:]*')
    let source_arg = arg[len(source_name)+1 :]
    let source_args = source_arg  == '' ? [] :
          \  map(split(source_arg, '\\\@<!:', 1),
          \      'substitute(v:val, ''\\\(.\)'', "\\1", "g")')
    call add(_, { 'name': source_name, 'args': source_args })
  endfor

  return [_, options]
endfunction"}}}

" vim: foldmethod=marker
