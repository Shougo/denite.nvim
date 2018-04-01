" set verbose=1

let s:suite = themis#suite('custom')
let s:assert = themis#helper('assert')

function! s:suite.before_each() abort
  call denite#custom#_init()
endfunction

function! s:suite.init_context() abort
  let context = denite#init#_context({'force_quit': v:true})
  call s:assert.equals(context['post_action'], 'quit')

  let context = denite#init#_context({'quit': v:false})
  call s:assert.equals(context['post_action'], 'open')

  let context = denite#init#_context({'short_source_names': v:true})
  call s:assert.equals(context['source_names'], 'short')
endfunction
