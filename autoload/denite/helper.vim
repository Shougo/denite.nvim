"=============================================================================
" FILE: helper.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#helper#complete(arglead, cmdline, cursorpos) abort "{{{
  let ret = s:parse_options_args(a:cmdline)[0]
  let source_name = ret[-1][0]
  let source_args = ret[-1][1:]

  let _ = []

  if a:arglead !~ ':'
    " Option names completion.
    let _ += copy(denite#helper#options())

    " Source name completion.
    let _ += map(globpath(&runtimepath,
          \ 'rplugin/python3/denite/source/*.py', 1, 1),
          \ "fnamemodify(v:val, ':t:r')")
  endif

  return sort(filter(_, 'stridx(v:val, a:arglead) == 0'))
endfunction"}}}

function! denite#helper#call_denite(command, args, line1, line2) abort "{{{
  let [args, context] = s:parse_options_args(a:args)

  let context.firstline = a:line1
  let context.lastline = a:line2
  let context.bufnr = bufnr('%')

  echomsg string(args)
  call denite#start(args, context)
endfunction"}}}

function! denite#helper#options() abort "{{{
  return []
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

    let name = substitute(tr(arg_key, '-', '_'), '=$', '', '')
    let value = (arg_key =~ '=$') ? arg[len(arg_key) :] : 1

    if arg_key =~ '^-custom-'
          \ || index(denite#helper#options(), arg_key) >= 0
      let options[name[1:]] = value
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
