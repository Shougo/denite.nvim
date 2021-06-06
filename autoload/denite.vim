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

function! denite#do_targets(action_name, candidates, ...) abort
  let context = denite#init#_user_options()
  call extend(context, get(a:000, 0, {}))
  let args = [context, a:action_name, denite#util#convert2list(a:candidates)]
  return denite#util#rpcrequest('_denite_do_targets', args, v:false)
endfunction

function! denite#do_map(name, ...) abort
  let args = denite#util#convert2list(get(a:000, 0, []))
  let esc = (mode() ==# 'i' ? "\<C-o>" : '')
  return printf(esc . ":\<C-u>call denite#_call_map(%s, %s, %s)\<CR>",
        \ string(a:name), 'v:false', string(args))
endfunction
function! denite#_call_map(name, is_async, args) abort
  let is_filter = &l:filetype ==# 'denite-filter'

  if is_filter
    call denite#filter#_move_to_parent(v:true)
  endif

  if &l:filetype !=# 'denite'
    return
  endif

  let args = denite#util#convert2list(a:args)

  call denite#util#rpcrequest(
        \ (a:is_async ? '_denite_do_async_map' : '_denite_do_map'),
        \ [bufnr('%'), a:name, args], a:is_async)

  if is_filter
    call s:update_filter()
  endif
endfunction
function! denite#_update_map(name, bufnr, is_async) abort
  let is_filter = &l:filetype ==# 'denite-filter'

  try
    call denite#util#rpcrequest(
          \ (a:is_async ? '_denite_do_async_map' : '_denite_do_map'),
          \ [a:bufnr, a:name, []], a:is_async)
  catch
    " Ignore RPC errors
  endtry

  if is_filter
    call s:update_filter()
  endif
endfunction
function! s:update_filter() abort
  let denite_statusline = getbufvar(g:denite#_filter_parent,
        \ 'denite_statusline', {})

  if win_getid() != g:denite#_filter_winid
    noautocmd call win_gotoid(g:denite#_filter_winid)
  endif

  if &l:filetype ==# 'denite-filter'
    resize 1
    let b:denite_statusline = denite_statusline
  else
    stopinsert
  endif
endfunction
function! denite#call_map(name, ...) abort
  call denite#_call_map(a:name, v:false, get(a:000, 0, []))
endfunction
function! denite#call_async_map(name, ...) abort
  call denite#_call_map(a:name, v:true, get(a:000, 0, []))
endfunction

" For mapping functions
function! denite#move_to_filter() abort
  call win_gotoid(g:denite#_filter_winid)
  return ''
endfunction
function! denite#move_to_parent() abort
  call denite#filter#_move_to_parent(v:false)
  return ''
endfunction
function! denite#increment_parent_cursor(inc) abort
  let ids = win_findbuf(g:denite#_filter_parent)
  if empty(ids) || !exists('*nvim_win_get_cursor')
    return ''
  endif

  let cursor = nvim_win_get_cursor(ids[0])
  let row = max([min([cursor[0] + a:inc,
        \ nvim_buf_line_count(g:denite#_filter_parent)]), 1])
  call nvim_win_set_cursor(ids[0], [row, cursor[1]])
  redraw!
  return ''
endfunction
