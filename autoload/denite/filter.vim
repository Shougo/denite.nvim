"=============================================================================
" FILE: filter.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#filter#open(parent, input) abort
  let id = exists('g:denite#_filter_bufnr') ?
        \ win_findbuf(g:denite#_filter_bufnr) : []
  if !empty(id)
    call win_gotoid(id[0])
    call cursor(line('$'), 0)
  else
    split denite-filter
    let g:denite#_filter_winid = win_getid()
    let g:denite#_filter_bufnr = bufnr('%')
  endif

  let g:denite#_filter_parent = a:parent

  call denite#filter#init_buffer()

  " Set the current input
  if getline('$') ==# ''
    call setline('$', a:input)
  else
    call append('$', a:input)
  endif

  call cursor(line('$'), 0)
  startinsert!
endfunction

function! denite#filter#init_buffer() abort
  setlocal hidden
  setlocal bufhidden=hide
  setlocal buftype=nofile

  resize 1

  setfiletype denite-filter

  nnoremap <buffer><silent> <Plug>(denite_filter_update)
        \ :<C-u>call <SID>update()<CR>:call <SID>quit()<CR>
  inoremap <buffer><silent> <Plug>(denite_filter_update)
        \ <ESC>:call <SID>update()<CR>:call <SID>quit()<CR>
  nnoremap <buffer><silent> <Plug>(denite_filter_quit)
        \ :<C-u>call <SID>quit()<CR>

  nmap <buffer> <CR> <Plug>(denite_filter_update)
  nmap <buffer> q    <Plug>(denite_filter_quit)
  imap <buffer> <CR> <Plug>(denite_filter_update)

  call timer_start(1500, {-> s:update()}, {'repeat': -1})
endfunction

function! s:update() abort
  if &filetype !=# 'denite-filter' || mode() !=# 'i'
    return
  endif

  let input = getline('.')

  call s:move_to_parent()

  call denite#call_map('filter', input)

  call win_gotoid(g:denite#_filter_winid)
endfunction

function! s:quit() abort
  if winnr('$') ==# 1
    buffer #
  else
    close!
  endif

  call s:move_to_parent()
endfunction

function! s:move_to_parent() abort
  let id = win_findbuf(g:denite#_filter_parent)
  if empty(id)
    return
  endif

  call win_gotoid(id[0])
endfunction
