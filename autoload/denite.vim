"=============================================================================
" FILE: denite.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! denite#initialize() abort "{{{
  return denite#init#_initialize()
endfunction"}}}
function! denite#start(sources, ...) abort "{{{
  let user_context = get(a:000, 0, {})
  let buffer_name = get(user_context, 'buffer_name', 'default')

  let context = extend(denite#init#_context(), denite#init#_user_options())
  let context.custom = denite#custom#get()
  if has_key(context.custom.option, buffer_name)
    call extend(context, context.custom.option[buffer_name])
  endif
  call extend(context, user_context)

  if denite#initialize()
    return
  endif

  if has('nvim')
    return _denite_start(a:sources, context)
  else
    return denite#vim#_start(a:sources, context)
  endif
endfunction"}}}

" vim: foldmethod=marker
