"=============================================================================
" FILE: denite.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! s:check_required_python() abort
  if has('python3')
    call s:report_ok('has("python3") was successful')
  else
    call s:report_error('has("python3") was not successful')
  endif

  if !denite#init#_python_version_check()
    call s:report_ok('Python 3.6.1+ was successful')
  else
    call s:report_error(
          \ 'Python 3.6.1+ was not successful',
          \ 'Please use Python 3.6.1+.')
  endif
endfunction

function! s:check_required_msgpack() abort
  if !denite#init#_msgpack_version_check()
    call s:report_ok('Require msgpack 1.0.0+ was successful')
  else
    call s:report_error(
          \ 'Require msgpack 1.0.0+ was not successful',
          \ 'Please install/upgrade msgpack 1.0.0+.')
  endif
endfunction

function! health#denite#check() abort
  call s:report_start('denite.nvim')

  call s:check_required_python()
  call s:check_required_msgpack()
endfunction

function! s:report_start(report) abort
  if has('nvim-0.10')
    call v:lua.vim.health.start(a:report)
  else
    call health#report_start(a:report)
  endif
endfunction

function! s:report_ok(report) abort
  if has('nvim-0.10')
    call v:lua.vim.health.ok(a:report)
  else
    call health#report_ok(a:report)
  endif
endfunction

function! s:report_error(report) abort
  if has('nvim-0.10')
    call v:lua.vim.health.error(a:report)
  else
    call health#report_error(a:report)
  endif
endfunction
