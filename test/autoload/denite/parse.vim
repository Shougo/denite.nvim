" set verbose=1

let s:suite = themis#suite('parse')
let s:assert = themis#helper('assert')

let s:path = tempname()

function! s:suite.parse_options_args() abort
  call s:assert.equals(denite#helper#_parse_options_args(
        \ 'foo:bar bar:baz'), [[
        \ {'name': 'foo', 'args': ['bar']},
        \ {'name': 'bar', 'args': ['baz']}
        \ ], {}])

  call s:assert.equals(denite#helper#_parse_options_args(
        \ 'foo:bar\:baz'), [[
        \ {'name': 'foo', 'args': ['bar:baz']},
        \ ], {}])
endfunction
