"=============================================================================
" FILE: filter.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#filter#open(context, parent, entire_len, is_async) abort
  let id = win_findbuf(g:denite#_filter_bufnr)
  if !empty(id)
    call win_gotoid(id[0])
    call cursor(line('$'), 0)
  else
    call s:new_filter_buffer(a:context)
  endif

  let g:denite#_filter_parent = a:parent
  let g:denite#_filter_entire_len = a:entire_len

  call denite#filter#init_buffer()

  " Set the current input
  if getline('$') ==# ''
    call setline('$', a:context['input'])
  else
    call append('$', a:context['input'])
  endif

  call s:stop_timer()

  if !a:is_async && g:denite#_filter_entire_len <
        \ a:context['max_dynamic_update_candidates']
    let g:denite#_filter_timer = timer_start(500,
          \ {-> s:update()}, {'repeat': -1})
  endif

  augroup denite-filter
    autocmd!
    autocmd InsertLeave <buffer> call s:update()
    autocmd WinLeave <buffer> call s:quit()
  augroup END

  call cursor(line('$'), 0)
  startinsert!
endfunction

function! denite#filter#init_buffer() abort
  setlocal bufhidden=hide
  setlocal buftype=nofile
  setlocal colorcolumn=
  setlocal foldcolumn=0
  setlocal hidden
  setlocal nobuflisted
  setlocal nofoldenable
  setlocal nolist
  setlocal nomodeline
  setlocal nonumber
  setlocal norelativenumber
  setlocal nospell
  setlocal noswapfile
  setlocal nowrap
  setlocal winfixheight

  resize 1

  setfiletype denite-filter

  nnoremap <buffer><silent> <Plug>(denite_filter_update)
        \ :<C-u>call <SID>async_update()<CR>
  inoremap <buffer><silent> <Plug>(denite_filter_update)
        \ <ESC>:call <SID>async_update()<CR>
  nnoremap <buffer><silent> <Plug>(denite_filter_quit)
        \ :<C-u>call <SID>quit()<CR>

  nmap <buffer> <CR> <Plug>(denite_filter_update)
  nmap <buffer> q    <Plug>(denite_filter_quit)
  imap <buffer> <CR> <Plug>(denite_filter_update)
endfunction

function! s:new_filter_buffer(context) abort
  if a:context['split'] ==# 'floating' && exists('*nvim_open_win')
    let gap = a:context['max_source_name']
    call nvim_open_win(bufnr('%'), v:true, {
          \ 'relative': 'editor',
          \ 'row': a:context['winrow'] + a:context['winheight'],
          \ 'col': a:context['wincol'] + a:context['max_source_name'] + gap,
          \ 'width': (a:context['winwidth'] -
          \           a:context['max_source_name'] - gap),
          \ 'height': 1,
          \})
    edit denite-filter
  else
    execute a:context['filter_split_direction'] 'split' 'denite-filter'
  endif
  let g:denite#_filter_winid = win_getid()
  let g:denite#_filter_bufnr = bufnr('%')
endfunction

function! s:update() abort
  if &filetype !=# 'denite-filter'
    return
  endif

  let input = getline('.')

  call s:move_to_parent()

  silent! call denite#call_map('filter', input)

  call win_gotoid(g:denite#_filter_winid)
endfunction

function! s:async_update() abort
  if &filetype !=# 'denite-filter'
    return
  endif

  let input = getline('.')

  call s:quit()

  call denite#call_async_map('filter', input)
endfunction

function! s:quit() abort
  if winnr('$') ==# 1
    buffer #
  else
    close!
  endif

  call s:move_to_parent()

  call s:stop_timer()
endfunction

function! s:move_to_parent() abort
  let id = win_findbuf(g:denite#_filter_parent)
  if empty(id)
    return
  endif

  noautocmd call win_gotoid(id[0])
endfunction

function! s:stop_timer() abort
  if exists('g:denite#_filter_timer')
    call timer_stop(g:denite#_filter_timer)
    unlet g:denite#_filter_timer
  endif
endfunction
