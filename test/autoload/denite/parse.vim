" set verbose=1

let s:suite = themis#suite('parse')
let s:assert = themis#helper('assert')

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

  call s:assert.equals(denite#helper#_parse_options_args(
        \ 'file/rec:''foo:bar'''), [[
        \ {'name': 'file/rec', 'args': ['foo:bar']},
        \ ], {}])

  call s:assert.equals(denite#helper#_parse_options_args(
        \ 'file/rec:"foo:bar"'), [[
        \ {'name': 'file/rec', 'args': ['foo:bar']},
        \ ], {}])

  call s:assert.equals(denite#helper#_parse_options_args(
        \ '-do="hoge" file/rec:"foo:bar"'), [[
        \ {'name': 'file/rec', 'args': ['foo:bar']},
        \ ], {'do': 'hoge'}])

  call s:assert.equals(denite#helper#_parse_options_args(
        \ '-path=c:\\FolderX\\FolderY file/rec:'), [[
        \ {'name': 'file/rec', 'args': []},
        \ ], {'path': 'c:\FolderX\FolderY'}])

  call s:assert.equals(denite#helper#_parse_options_args(
        \ '-path=''c:\FolderX\FolderY'' file/rec:'), [[
        \ {'name': 'file/rec', 'args': []},
        \ ], {'path': 'c:\FolderX\FolderY'}])
endfunction
