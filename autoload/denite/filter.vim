"=============================================================================
" FILE: filter.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#filter#_open(context, parent, entire_len, is_async) abort
  let id = win_findbuf(g:denite#_filter_bufnr)
  if !empty(id)
    call win_gotoid(id[0])
    call cursor(line('$'), 0)
  else
    call s:new_filter_buffer(a:context)
  endif

  let g:denite#_filter_parent = a:parent
  let g:denite#_filter_entire_len = a:entire_len

  call s:init_buffer()

  " Set the current input
  if getline('$') ==# ''
    call setline('$', a:context['input'])
  else
    call append('$', a:context['input'])
  endif

  if a:context['prompt'] !=# ''
    execute printf('sign define denite_filter_prompt text=%s texthl=%s',
          \ a:context['prompt'][:1], a:context['highlight_prompt'])
    execute 'silent! sign unplace 2000 buffer=' . bufnr('%')
    execute printf('sign place 2000 name=denite_filter_prompt'.
         \ ' line=%d buffer=%d', line('$'), bufnr('%'))
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
  augroup END

  call cursor(line('$'), 0)
  startinsert!
endfunction

function! s:init_buffer() abort
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
    call nvim_open_win(bufnr('%'), v:true, {
          \ 'relative': 'editor',
          \ 'row': a:context['winrow'] + a:context['winheight'],
          \ 'col': str2nr(a:context['wincol']),
          \ 'width': str2nr(a:context['winwidth']),
          \ 'height': 1,
          \})
    edit denite-filter
    let &l:winhighlight = 'Normal:' . a:context['highlight_filter_background']
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

  call denite#filter#_move_to_parent(v:true)

  silent! call denite#call_map('filter', input)

  noautocmd call win_gotoid(g:denite#_filter_winid)
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

  call denite#filter#_move_to_parent(v:false)

  call s:stop_timer()
endfunction

function! denite#filter#_move_to_parent(is_async) abort
  let id = win_findbuf(g:denite#_filter_parent)
  if empty(id)
    return
  endif

  if a:is_async
    " Note: noautocmd for statusline flicker
    noautocmd call win_gotoid(id[0])
  else
    call win_gotoid(id[0])
  endif
endfunction

function! s:stop_timer() abort
  if exists('g:denite#_filter_timer')
    call timer_stop(g:denite#_filter_timer)
    unlet g:denite#_filter_timer
  endif
endfunction
