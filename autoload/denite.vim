"=============================================================================
" FILE: denite.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#initialize() abort
  return denite#init#_initialize()
endfunction
function! denite#start(sources, ...) abort
  call inputsave()
  try
    let user_context = get(a:000, 0, {})
    return s:start(a:sources, user_context)
  finally
    call inputrestore()
  endtry
endfunction

" Statusline functions
function! denite#get_status(name) abort
  return !exists('b:denite_statusline') ? '' :
        \ get(b:denite_statusline, a:name, '')
endfunction

function! s:start(sources, user_context) abort
  if denite#initialize()
    return
  endif

  " Add current position to the jumplist.
  let pos = getpos('.')
  execute line('.')
  call setpos('.', pos)

  let args = [a:sources, a:user_context]
  return denite#util#rpcrequest('_denite_start', args, v:false)
endfunction

function! denite#do_action(context, action_name, targets) abort
  let args = [a:context, a:action_name, a:targets]
  return denite#util#rpcrequest('_denite_do_action', args, v:false)
endfunction

function! denite#do_map(name, ...) abort
  if &l:filetype !=# 'denite'
    return ''
  endif

  let args = denite#util#convert2list(get(a:000, 0, []))
  return printf(":\<C-u>call denite#call_map(%s, %s)\<CR>",
        \ string(a:name), string(args))
endfunction
function! denite#call_map(name, ...) abort
  if &l:filetype !=# 'denite'
    return
  endif

  let args = denite#util#convert2list(get(a:000, 0, []))
  call denite#util#rpcrequest(
        \ '_denite_do_map', [a:name, args], v:false)
endfunction
