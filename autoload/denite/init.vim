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

function! denite#init#_context(user_context) abort
  let buffer_name = get(a:user_context, 'buffer_name', 'default')
  let context = s:internal_options()
  call extend(context, denite#init#_user_options())
  let context.custom = denite#custom#_get()
  if has_key(context.custom.option, '_')
    call extend(context, context.custom.option['_'])
  endif
  if has_key(context.custom.option, buffer_name)
    call extend(context, context.custom.option[buffer_name])
  endif
  call extend(context, a:user_context)

  " For compatibility(deprecated variables)
  for [old_option, new_option] in filter(items(
        \ denite#init#_deprecated_options()),
        \ "has_key(context, v:val[0]) && v:val[1] !=# ''")
    let context[new_option] = context[old_option]
  endfor
  if get(context, 'short_source_names', v:false)
    let context['source_names'] = 'short'
  endif
  if has_key(context, 'quit') && !context['quit']
    let context['post_action'] = 'open'
  endif
  if get(context, 'force_quit', v:false)
    let context['post_action'] = 'quit'
  endif

  return context
endfunction
function! s:internal_options() abort
  return {
        \ 'encoding': &encoding,
        \ 'error_messages': [],
        \ 'is_windows': ((has('win32') || has('win64')) ? v:true : v:false),
        \ 'messages': [],
        \ 'prev_winid': win_getid(),
        \ 'has_preview_window': len(filter(range(1, winnr('$')),
        \   'getwinvar(v:val, ''&previewwindow'')')) > 0,
        \ 'quick_move_table': {
        \   'a' : 0, 's' : 1, 'd' : 2, 'f' : 3, 'g' : 4,
        \   'h' : 5, 'j' : 6, 'k' : 7, 'l' : 8, ';' : 9,
        \   'q' : 10, 'w' : 11, 'e' : 12, 'r' : 13, 't' : 14,
        \   'y' : 15, 'u' : 16, 'i' : 17, 'o' : 18, 'p' : 19,
        \   '1' : 20, '2' : 21, '3' : 22, '4' : 23, '5' : 24,
        \   '6' : 25, '7' : 26, '8' : 27, '9' : 28, '0' : 29,
        \ },
        \ 'runtimepath': &runtimepath,
        \ 'selected_icon': '*',
        \}
endfunction
function! denite#init#_user_options() abort
  return {
        \ 'auto_accel': v:false,
        \ 'auto_highlight': v:false,
        \ 'auto_preview': v:false,
        \ 'auto_resize': v:false,
        \ 'auto_resume': v:false,
        \ 'buffer_name': 'default',
        \ 'cursor_pos': '',
        \ 'cursor_wrap': v:false,
        \ 'cursor_shape': (has('gui_running') ? v:true : v:false),
        \ 'cursorline': v:true,
        \ 'default_action': 'default',
        \ 'direction': 'botright',
        \ 'do': '',
        \ 'empty': v:true,
        \ 'highlight_cursor': 'Cursor',
        \ 'highlight_matched_range': 'Underlined',
        \ 'highlight_matched_char': 'Search',
        \ 'highlight_mode_normal': 'WildMenu',
        \ 'highlight_mode_insert': 'CursorLine',
        \ 'highlight_preview_line': 'Search',
        \ 'ignorecase': v:true,
        \ 'immediately': v:false,
        \ 'immediately_1': v:false,
        \ 'input': '',
        \ 'matchers': '',
        \ 'max_candidate_width': 200,
        \ 'mode': '',
        \ 'path': getcwd(),
        \ 'previewheight': &previewheight,
        \ 'prompt': '#',
        \ 'prompt_highlight': 'Statement',
        \ 'post_action': 'none',
        \ 'refresh': v:false,
        \ 'resume': v:false,
        \ 'reversed': v:false,
        \ 'root_markers': '',
        \ 'scroll': 0,
        \ 'smartcase': v:false,
        \ 'sorters': '',
        \ 'split': 'horizontal',
        \ 'source_names': '',
        \ 'statusline': v:true,
        \ 'updatetime': 100,
        \ 'skiptime': 500,
        \ 'unique': v:false,
        \ 'use_default_mappings': v:true,
        \ 'vertical_preview': v:false,
        \ 'winheight': 20,
        \ 'winwidth': 90,
        \ 'winminheight': -1,
        \}
endfunction
function! denite#init#_deprecated_options() abort
  return {
        \ 'select': 'cursor_pos',
        \ 'force_quit': '',
        \ 'quit': '',
        \}
endfunction
