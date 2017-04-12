"=============================================================================
" FILE: init.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

if !exists('s:is_enabled')
  let s:is_enabled = 0
endif

function! s:is_initialized() abort
  return exists('g:denite#_channel_id')
endfunction

function! denite#init#_initialize() abort
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
endfunction

function! denite#init#_context() abort
  return {
        \ 'runtimepath': &runtimepath,
        \ 'encoding': &encoding,
        \ 'is_windows': has('win32') || has('win64'),
        \ 'selected_icon': '*',
        \ 'messages': [],
        \}
endfunction
function! denite#init#_user_options() abort
  return {
        \ 'auto_highlight': v:false,
        \ 'auto_preview': v:false,
        \ 'auto_resize': v:false,
        \ 'buffer_name': 'default',
        \ 'cursor_pos': '',
        \ 'cursor_wrap': v:false,
        \ 'cursorline': v:true,
        \ 'default_action': 'default',
        \ 'direction': 'botright',
        \ 'empty': v:true,
        \ 'highlight_cursor': 'Cursor',
        \ 'highlight_matched_range': 'Underlined',
        \ 'highlight_matched_char': 'Search',
        \ 'highlight_mode_normal': 'WildMenu',
        \ 'highlight_mode_insert': 'CursorLine',
        \ 'ignorecase': v:true,
        \ 'immediately': v:false,
        \ 'input': '',
        \ 'max_candidate_width': 200,
        \ 'mode': '',
        \ 'path': getcwd(),
        \ 'previewheight': &previewheight,
        \ 'prompt': '#',
        \ 'prompt_highlight': 'Statement',
        \ 'quit': v:true,
        \ 'refresh': v:false,
        \ 'resume': v:false,
        \ 'reversed': v:false,
        \ 'scroll': 0,
        \ 'short_source_names': v:false,
        \ 'statusline': v:true,
        \ 'updatetime': 100,
        \ 'use_default_mappings': v:true,
        \ 'vertical_preview': v:false,
        \ 'winheight': 20,
        \ 'winminheight': -1,
        \}
endfunction
function! denite#init#_deprecated_options() abort
  return {
        \ 'select': 'cursor_pos',
        \}
endfunction
