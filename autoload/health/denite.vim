"=============================================================================
" FILE: denite.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! s:check_required_python() abort
  if has('python3')
    call health#report_ok('has("python3") was successful')
  else
    call health#report_error('has("python3") was not successful')
  endif

  if !denite#init#_python_version_check()
    call health#report_ok('Python 3.6.1+ was successful')
  else
    call health#report_error(
          \ 'Python 3.6.1+ was not successful',
          \ 'Please use Python 3.6.1+.')
  endif
endfunction

function! s:check_required_msgpack() abort
  if !denite#init#_msgpack_version_check()
    call health#report_ok('Require msgpack 1.0.0+ was successful')
  else
    call health#report_error(
          \ 'Require msgpack 1.0.0+ was not successful',
          \ 'Please install/upgrade msgpack 1.0.0+.')
  endif
endfunction

function! health#denite#check() abort
  call health#report_start('denite.nvim')

  call s:check_required_python()
  call s:check_required_msgpack()
endfunction
