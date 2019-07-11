"=============================================================================
" FILE: init.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

if !exists('s:is_enabled')
  let s:is_enabled = 0
endif

function! denite#init#_check_channel() abort
  return exists('g:denite#_channel_id')
endfunction

function! denite#init#_initialize() abort
  if denite#init#_check_channel()
    return
  endif

  augroup denite
    autocmd!
  augroup END

  if !has('python3')
    call denite#util#print_error(
          \ 'denite.nvim does not work with this version.')
    call denite#util#print_error(
          \ 'It requires Neovim with Python3 support("+python3").')
    return 1
  endif

  if has('nvim') && !has('nvim-0.3.0')
    call denite#util#print_error(
          \ 'denite.nvim requires nvim +v0.3.0.')
    return 1
  endif

  try
    if denite#util#has_yarp()
      let g:denite#_yarp = yarp#py3('denite')
      call g:denite#_yarp.request('_denite_init')
      let g:denite#_channel_id = 1
    else
      " rplugin.vim may not be loaded on VimEnter
      if !exists('g:loaded_remote_plugins')
        runtime! plugin/rplugin.vim
      endif
      call _denite_init()
    endif
    call s:initialize_variables()
  catch
    call denite#util#print_error(v:exception)
    call denite#util#print_error(v:throwpoint)

    if denite#util#has_yarp()
      if !has('nvim') && !exists('*neovim_rpc#serveraddr')
        call denite#util#print_error(
              \ 'denite requires vim-hug-neovim-rpc plugin in Vim.')
      endif

      if !exists('*yarp#py3')
        call denite#util#print_error(
              \ 'denite requires nvim-yarp plugin.')
      endif
    else
      call denite#util#print_error(
          \ 'denite failed to load. '
          \ .'Try the :UpdateRemotePlugins command and restart Neovim. '
          \ .'See also :checkhealth.')
    endif
    return 1
  endtry
endfunction
function! s:initialize_variables() abort
  let g:denite#_filter_winid = -1
  let g:denite#_previewed_buffers = {}
  let g:denite#_candidates = []
  let g:denite#_ret = {}
  let g:denite#_async_ret = {}
  let g:denite#_filter_bufnr = -1
  let g:denite#_serveraddr =
        \ denite#util#has_yarp() ?
        \ neovim_rpc#serveraddr() : v:servername
  if g:denite#_serveraddr ==# ''
    " Use NVIM_LISTEN_ADDRESS
    let g:denite#_serveraddr = $NVIM_LISTEN_ADDRESS
  endif
endfunction

function! denite#init#_user_options() abort
  return {
        \ 'auto_action': '',
        \ 'auto_resize': v:false,
        \ 'auto_resume': v:false,
        \ 'buffer_name': 'default',
        \ 'cursor_pos': '',
        \ 'cursorline': v:true,
        \ 'default_action': 'default',
        \ 'direction': 'botright',
        \ 'do': '',
        \ 'empty': v:true,
        \ 'expand': v:false,
        \ 'filter_split_direction': 'botright',
        \ 'filter_updatetime': 100,
        \ 'highlight_filter_background': 'NormalFloat',
        \ 'highlight_matched_range': 'Underlined',
        \ 'highlight_matched_char': 'Search',
        \ 'highlight_preview_line': 'Search',
        \ 'highlight_prompt': 'Special',
        \ 'highlight_window_background': 'NormalFloat',
        \ 'ignorecase': v:true,
        \ 'immediately': v:false,
        \ 'immediately_1': v:false,
        \ 'input': '',
        \ 'matchers': '',
        \ 'max_candidate_width': 200,
        \ 'max_dynamic_update_candidates': 20000,
        \ 'path': getcwd(),
        \ 'previewheight': &previewheight,
        \ 'prompt': '',
        \ 'post_action': 'none',
        \ 'quick_move': '',
        \ 'refresh': v:false,
        \ 'resume': v:false,
        \ 'reversed': v:false,
        \ 'root_markers': '',
        \ 'smartcase': v:false,
        \ 'sorters': '',
        \ 'split': 'horizontal',
        \ 'source_names': '',
        \ 'start_filter': v:false,
        \ 'statusline': v:true,
        \ 'unique': v:false,
        \ 'vertical_preview': v:false,
        \ 'wincol': &columns / 4,
        \ 'winheight': 20,
        \ 'winrow': &lines / 2 - 10,
        \ 'winwidth': &columns / 2,
        \ 'winminheight': -1,
        \}
endfunction
function! denite#init#_deprecated_options() abort
  return {}
endfunction

function! denite#init#_python_version_check() abort
  python3 << EOF
import vim
import sys
vim.vars['denite#_python_version_check'] = (
    sys.version_info.major,
    sys.version_info.minor,
    sys.version_info.micro) < (3, 6, 1)
EOF
  return g:denite#_python_version_check
endfunction
