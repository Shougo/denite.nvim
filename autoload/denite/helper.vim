"=============================================================================
" FILE: helper.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#helper#complete(arglead, cmdline, cursorpos) abort
  let _ = []

  if a:arglead =~# ':'
    " Todo: source arguments completion.
  elseif a:arglead =~# '^-'
    " Option names completion.
    let bool_options = keys(filter(copy(denite#init#_user_options()),
          \ 'type(v:val) == type(v:true) || type(v:val) == type(v:false)'))
    let _ += map(copy(bool_options), "'-' . tr(v:val, '_', '-')")
    let string_options = keys(filter(copy(denite#init#_user_options()),
          \ 'type(v:val) != type(v:true) && type(v:val) != type(v:false)'))
    let _ += map(copy(string_options), "'-' . tr(v:val, '_', '-') . '='")

    " Add "-no-" option names completion.
    let _ += map(copy(bool_options), "'-no-' . tr(v:val, '_', '-')")
  else
    " Source name completion.
    let _ += filter(map(globpath(&runtimepath,
          \             'rplugin/python3/denite/source/*.py', 1, 1),
          \             "fnamemodify(v:val, ':t:r')"),
          \         "v:val !=# 'base' && v:val !=# '__init__'")
  endif

  return uniq(sort(filter(_, 'stridx(v:val, a:arglead) == 0')))
endfunction
function! denite#helper#complete_actions(arglead, cmdline, cursorpos) abort
  return uniq(sort(filter(copy(g:denite#_actions),
        \ 'stridx(v:val, a:arglead) == 0')))
endfunction

function! denite#helper#call_denite(command, args, line1, line2) abort
  let [args, context] = denite#helper#_parse_options_args(a:args)

  let context.firstline = a:line1
  let context.lastline = a:line2
  let context.bufnr = bufnr('%')
  if a:command ==# 'DeniteCursorWord'
    let context.input = expand('<cword>')
  elseif a:command ==# 'DeniteBufferDir'
    let context.path = fnamemodify(bufname('%'), ':p:h')
  elseif a:command ==# 'DeniteProjectDir'
    let context.path = denite#util#path2project_directory(
          \ get(context, 'path', getcwd()))
  endif

  call denite#start(args, context)
endfunction

function! denite#helper#preview_file(context, filename) abort
  if a:context.vertical_preview
    let denite_winwidth = &columns
    call denite#util#execute_path('silent vertical pedit!', a:filename)
    wincmd P
    execute 'vert resize ' . (denite_winwidth / 2)
  else
    let previewheight_save = &previewheight
    try
      let &previewheight = a:context.previewheight
      call denite#util#execute_path('silent pedit!', a:filename)
    finally
      let &previewheight = previewheight_save
    endtry
  endif
endfunction

function! denite#helper#options() abort
  return map(keys(denite#init#_user_options()), "tr(v:val, '_', '-')")
endfunction

function! denite#helper#_parse_options_args(cmdline) abort
  let _ = []
  let [args, options] = s:parse_options(a:cmdline)

  for arg in args
    " Add source name.
    let source_name = matchstr(arg, '^[^:]*')
    let source_arg = arg[len(source_name)+1 :]
    let source_args = []
    if source_arg !=# ''
      for s in split(source_arg, s:re_unquoted_match('\\\@<!:'), 1)
        let s = substitute(s, '\\\(.\)', "\\1", 'g')

        " remove leading/ending quote pairs
        if s[0] ==# '"' && s[len(s) - 1] ==# '"'
          let s = s[1: len(s) - 2]
        endif
        if s[0] ==# "'" && s[len(s) - 1] ==# "'"
          let s = s[1: len(s) - 2]
        endif

        call add(source_args, s)
      endfor
    endif
    call add(_, { 'name': source_name, 'args': source_args })
  endfor

  return [_, options]
endfunction
function! s:re_unquoted_match(match) abort
  " Don't match a:match if it is located in-between unescaped single or double
  " quotes
  return a:match . '\v\ze([^"' . "'" . '\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"|'
        \ . "'" . '([^' . "'" . '\\]*\\.)*[^' . "'" . '\\]*' . "'" . '))*[^"'
        \ . "'" . ']*$'
endfunction
function! s:parse_options(cmdline) abort
  let args = []
  let options = {}

  " Eval
  let cmdline = (a:cmdline =~# '\\\@<!`.*\\\@<!`') ?
        \ s:eval_cmdline(a:cmdline) : a:cmdline

  for arg in split(cmdline, s:re_unquoted_match('\%(\\\@<!\s\)\+'))
    let arg = substitute(arg, '\\\( \)', '\1', 'g')
    let arg_key = substitute(arg, '=\zs.*$', '', '')

    let name = substitute(tr(arg_key, '-', '_'), '=$', '', '')[1:]
    if name =~# '^no_'
      let name = name[3:]
      let value = 0
    else
      let value = (arg_key =~# '=$') ? arg[len(arg_key) :] : 1
    endif

    if index(keys(denite#init#_user_options())
          \ + keys(denite#init#_deprecated_options()), name) >= 0
      let options[name] = value
    else
      call add(args, arg)
    endif
  endfor

  return [args, options]
endfunction
function! s:eval_cmdline(cmdline) abort
  let cmdline = ''
  let prev_match = 0
  let match = match(a:cmdline, '\\\@<!`.\{-}\\\@<!`')
  while match >= 0
    if match - prev_match > 0
      let cmdline .= a:cmdline[prev_match : match - 1]
    endif
    let prev_match = matchend(a:cmdline,
          \ '\\\@<!`.\{-}\\\@<!`', match)
    let cmdline .= escape(eval(a:cmdline[match+1 : prev_match - 2]), '\ ')

    let match = match(a:cmdline, '\\\@<!`.\{-}\\\@<!`', prev_match)
  endwhile
  if prev_match >= 0
    let cmdline .= a:cmdline[prev_match :]
  endif

  return cmdline
endfunction

function! denite#helper#has_cmdline() abort
  if !exists('*getcompletion')
    return 0
  endif

  try
    call getcompletion('', 'cmdline')
  catch
    return 0
  endtry

  return 1
endfunction


function! denite#helper#_set_oldfiles(oldfiles) abort
  let v:oldfiles = a:oldfiles
endfunction
