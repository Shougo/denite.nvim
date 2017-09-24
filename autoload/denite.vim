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

function! denite#get_status_mode() abort
  return get(b:, 'denite_statusline_mode', '')
endfunction
function! denite#get_status_sources() abort
  return get(b:, 'denite_statusline_sources', '')
endfunction
function! denite#get_status_path() abort
  return get(b:, 'denite_statusline_path', '')
endfunction
function! denite#get_status_linenr() abort
  return get(b:, 'denite_statusline_linenr', '')
endfunction


function! s:start(sources, user_context) abort
  let buffer_name = get(a:user_context, 'buffer_name', 'default')

  let context = denite#init#_context()
  call extend(context, denite#init#_user_options())
  let context.custom = denite#custom#get()
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
        \ 'has_key(context, v:val[0])')
    let context[new_option] = context[old_option]
  endfor
  if get(context, 'short_source_names', v:false)
    let context['source_names'] = 'short'
  endif

  if denite#initialize()
    return
  endif

  " Add current position to the jumplist.
  let pos = getpos('.')
  execute line('.')
  call setpos('.', pos)

  return has('nvim') ? _denite_start(a:sources, context)
        \            : denite#vim#_start(a:sources, context)
endfunction

function! denite#do_action(context, action_name, targets) abort
  return has('nvim') ?
        \ _denite_do_action(a:context, a:action_name, a:targets) :
        \ denite#vim#_do_action(a:context, a:action_name, a:targets)
endfunction
