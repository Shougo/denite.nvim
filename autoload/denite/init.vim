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
  let g:denite#_default_mappings = {'_': {}, 'normal': {}, 'insert': {}}
  let default_mode_mappings = {
        \ "<Esc>": 'leave_mode',
        \ "<CR>":  'do_action:default',
        \ "<C-z>":  'suspend',
        \}
  let insert_mode_mappings = {
        \ "<C-h>": 'delete_backward_char',
        \ "<BS>": 'delete_backward_char',
        \ "<C-w>": 'delete_backward_word',
        \ "<C-u>": 'delete_backward_line',
        \ "<C-g>": 'move_to_next_line',
        \ "<Tab>": 'move_to_next_line',
        \ "<C-t>": 'move_to_prev_line',
        \ "<S-Tab>": 'move_to_prev_line',
        \ "<C-j>": 'input_command_line',
        \ "<C-r>": 'paste_from_register',
        \ "<C-l>": 'redraw',
        \ "<C-o>": 'enter_mode:normal',
        \ "<C-v>": 'do_action:preview',
        \}
  let normal_mode_mappings = {
        \ "i": 'enter_mode:insert',
        \ "j": 'move_to_next_line',
        \ "k": 'move_to_prev_line',
        \ "p": 'do_action:preview',
        \ "q": 'quit',
        \}
  for [char, value] in items(default_mode_mappings)
    let g:denite#_default_mappings._[char] = value
  endfor
  for [char, value] in items(insert_mode_mappings)
    let g:denite#_default_mappings.insert[char] = value
  endfor
  for [char, value] in items(normal_mode_mappings)
    let g:denite#_default_mappings.normal[char] = value
  endfor
endfunction"}}}

function! denite#init#_context() abort "{{{
  return {
        \ 'runtimepath': &runtimepath,
        \ 'encoding': &encoding,
        \ 'is_windows': has('win32') || has('win64'),
        \ 'mode': 'insert',
        \}
endfunction"}}}
function! denite#init#_user_options() abort "{{{
  return {
        \ 'auto_preview': v:false,
        \ 'buffer_name': 'default',
        \ 'cursor_highlight': 'Cursor',
        \ 'cursorline': v:true,
        \ 'default_action': 'default',
        \ 'empty': v:true,
        \ 'ignorecase': v:true,
        \ 'input': '',
        \ 'mode': 'insert',
        \ 'path': getcwd(),
        \ 'prompt': '#',
        \ 'prompt_highlight': 'Statement',
        \ 'quit': v:true,
        \ 'resume': v:false,
        \ 'statusline': v:true,
        \ 'winheight': 20,
        \}
endfunction"}}}

" vim: foldmethod=marker
