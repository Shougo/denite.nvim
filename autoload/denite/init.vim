"=============================================================================
" FILE: init.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

if !exists('s:is_enabled')
  let s:is_enabled = 0
endif

function! s:is_initialized() abort "{{{
  return exists('g:denite#_channel_id')
endfunction"}}}

function! denite#init#_initialize() abort "{{{
  if s:is_initialized()
    return
  endif

  augroup denite
    autocmd!
  augroup END

  if !has('nvim')
    return denite#vim#_initialize()
  endif

  if !has('python3')
    call denite#util#print_error(
          \ 'denite.nvim does not work with this version.')
    call denite#util#print_error(
          \ 'It requires Neovim with Python3 support("+python3").')
    return 1
  endif

  if !exists('*execute')
    call denite#util#print_error(
          \ 'denite.nvim does not work with this version.')
    call denite#util#print_error(
          \ 'It requires Neovim +v0.1.5.')
    return 1
  endif

  try
    if !exists('g:loaded_remote_plugins')
      runtime! plugin/rplugin.vim
    endif
    call _denite_init()
  catch
    call denite#util#print_error(
          \ 'denite.nvim is not registered as Neovim remote plugins.')
    call denite#util#print_error(
          \ 'Please execute :UpdateRemotePlugins command and restart Neovim.')
    return 1
  endtry

  call denite#init#_variables()
endfunction"}}}

function! denite#init#_variables() abort "{{{
  " Default mappings
  let g:denite#_default_mappings = {}
  let g:denite#_default_mappings._ = {}
  let default_mappings = {
        \ "\<Esc>": 'quit',
        \ "\<C-g>": 'quit',
        \ "\<C-h>": 'delete_backward_char',
        \ "\<BS>": 'delete_backward_char',
        \ "\<C-w>": 'delete_backward_word',
        \ "\<C-u>": 'delete_backward_line',
        \ "\<C-n>": 'move_to_next_line',
        \ "\<Tab>": 'move_to_next_line',
        \ "\<Down>": 'move_to_next_line',
        \ "\<C-p>": 'move_to_prev_line',
        \ "\<S-Tab>": 'move_to_prev_line',
        \ "\<Up>": 'move_to_prev_line',
        \ "\<C-j>": 'input_command_line',
        \ "\<CR>":  'do_action',
        \ "\<C-r>": 'paste_from_register',
        \}
  for [char, value] in items(default_mappings)
    let g:denite#_default_mappings._[denite#util#char2key(char)] = value
  endfor
endfunction"}}}

function! denite#init#_context() abort "{{{
  return {
        \ 'runtimepath': &runtimepath,
        \ 'encoding': &encoding,
        \ 'directory': getcwd(),
        \}
endfunction"}}}

" vim: foldmethod=marker
