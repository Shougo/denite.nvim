"=============================================================================
" FILE: util.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

let s:is_windows = has('win32') || has('win64')

function! denite#util#set_default(var, val, ...)  abort
  if !exists(a:var) || type({a:var}) != type(a:val)
    let alternate_var = get(a:000, 0, '')

    let {a:var} = exists(alternate_var) ?
          \ {alternate_var} : a:val
  endif
endfunction
function! denite#util#print_error(string) abort
  echohl Error | echomsg '[denite] ' . a:string | echohl None
endfunction
function! denite#util#print_warning(string) abort
  echohl WarningMsg | echomsg '[denite] ' . a:string | echohl None
endfunction

function! denite#util#convert2list(expr) abort
  return type(a:expr) ==# type([]) ? a:expr : [a:expr]
endfunction

function! denite#util#execute_path(command, path) abort
  let dir = s:path2directory(a:path)
  " Auto make directory.
  if dir !~# '^\a\+:' && !isdirectory(dir)
        \ && denite#util#input_yesno(
        \       printf('"%s" does not exist. Create?', dir))
    call mkdir(dir, 'p')
  endif

  let save_wildignore = &wildignore
  try
    execute a:command '`=s:expand(a:path)`'
    if &l:filetype ==# ''
      filetype detect
    endif
  catch /^Vim\%((\a\+)\)\=:E325/
    " Ignore swap file error
  catch
    call denite#util#print_error(v:throwpoint)
    call denite#util#print_error(v:exception)
  finally
    let &wildignore = save_wildignore
  endtry
endfunction
function! denite#util#execute_command(command) abort
  try
    execute a:command
  catch /^Vim\%((\a\+)\)\=:E/
    call denite#util#print_error(v:errmsg)
  endtry
endfunction

function! denite#util#echo(color, string) abort
  execute 'echohl' a:color
  echon a:string
  echohl NONE
endfunction

function! denite#util#open(filename) abort
  let filename = fnamemodify(a:filename, ':p')

  let s:is_unix = has('unix')
  let s:is_cygwin = has('win32unix')
  let s:is_mac = !s:is_windows && !s:is_cygwin
        \ && (has('mac') || has('macunix') || has('gui_macvim') ||
        \   (!isdirectory('/proc') && executable('sw_vers')))

  " Detect desktop environment.
  if s:is_windows
    " For URI only.
    " Note:
    "   # and % required to be escaped (:help cmdline-special)
    silent execute printf(
          \ '!start rundll32 url.dll,FileProtocolHandler %s',
          \ escape(filename, '#%'),
          \)
  elseif s:is_cygwin
    " Cygwin.
    call system(printf('%s %s', 'cygstart',
          \ shellescape(filename)))
  elseif executable('xdg-open')
    " Linux.
    call system(printf('%s %s &', 'xdg-open',
          \ shellescape(filename)))
  elseif executable('lemonade')
    call system(printf('%s %s &', 'lemonade open',
          \ shellescape(filename)))
  elseif exists('$KDE_FULL_SESSION') && $KDE_FULL_SESSION ==# 'true'
    " KDE.
    call system(printf('%s %s &', 'kioclient exec',
          \ shellescape(filename)))
  elseif exists('$GNOME_DESKTOP_SESSION_ID')
    " GNOME.
    call system(printf('%s %s &', 'gnome-open',
          \ shellescape(filename)))
  elseif executable('exo-open')
    " Xfce.
    call system(printf('%s %s &', 'exo-open',
          \ shellescape(filename)))
  elseif s:is_mac && executable('open')
    " Mac OS.
    call system(printf('%s %s &', 'open',
          \ shellescape(filename)))
  else
    " Give up.
    throw 'Not supported.'
  endif
endfunction

function! denite#util#split(string) abort
  return split(a:string, '\s*,\s*')
endfunction

function! denite#util#path2project_directory(path, ...) abort
  let is_allow_empty = get(a:000, 0, 0)
  let search_directory = s:path2directory(a:path)
  let directory = ''

  " Search VCS directory.
  for vcs in ['.git', '.bzr', '.hg', '.svn']
    if vcs ==# '.git'
      let directory = s:_path2project_directory_git(search_directory)
    elseif vcs ==# '.svn'
      let directory = s:_path2project_directory_svn(search_directory)
    else
      let directory = s:_path2project_directory_others(vcs, search_directory)
    endif
    if directory !=# ''
      break
    endif
  endfor

  " Search project file.
  if directory ==# ''
    for d in ['build.xml', 'prj.el', '.project', 'pom.xml', 'package.json',
          \ 'Makefile', 'configure', 'Rakefile', 'NAnt.build',
          \ 'P4CONFIG', 'tags', 'gtags']
      let d = findfile(d, s:escape_file_searching(search_directory) . ';')
      if d !=# ''
        let directory = fnamemodify(d, ':p:h')
        break
      endif
    endfor
  endif

  if directory ==# ''
    " Search /src/ directory.
    let base = s:substitute_path_separator(search_directory)
    if base =~# '/src/'
      let directory = base[: strridx(base, '/src/') + 3]
    endif
  endif

  if directory ==# '' && !is_allow_empty
    " Use original path.
    let directory = search_directory
  endif

  return s:substitute_path_separator(directory)
endfunction
function! s:path2directory(path) abort
  return s:substitute_path_separator(
        \ isdirectory(a:path) ? a:path : fnamemodify(a:path, ':p:h'))
endfunction
function! s:substitute_path_separator(path) abort
  return s:is_windows ? substitute(a:path, '\\', '/', 'g') : a:path
endfunction
function! s:escape_file_searching(buffer_name) abort
  return escape(a:buffer_name, '*[]?{}, ')
endfunction
function! s:_path2project_directory_git(path) abort
  let parent = a:path

  while 1
    let path = parent . '/.git'
    if isdirectory(path) || filereadable(path)
      return parent
    endif
    let next = fnamemodify(parent, ':h')
    if next == parent
      return ''
    endif
    let parent = next
  endwhile
endfunction
function! s:_path2project_directory_svn(path) abort
  let search_directory = a:path
  let directory = ''

  let find_directory = s:escape_file_searching(search_directory)
  let d = finddir('.svn', find_directory . ';')
  if d ==# ''
    return ''
  endif

  let directory = fnamemodify(d, ':p:h:h')

  " Search parent directories.
  let parent_directory = s:path2directory(
        \ fnamemodify(directory, ':h'))

  if parent_directory !=# ''
    let d = finddir('.svn', parent_directory . ';')
    if d !=# ''
      let directory = s:_path2project_directory_svn(parent_directory)
    endif
  endif
  return directory
endfunction
function! s:_path2project_directory_others(vcs, path) abort
  let vcs = a:vcs
  let search_directory = a:path

  let find_directory = s:escape_file_searching(search_directory)
  let d = finddir(vcs, find_directory . ';')
  if d ==# ''
    return ''
  endif
  return fnamemodify(d, ':p:h:h')
endfunction
function! s:expand(path) abort "{{{
  return s:substitute_path_separator(
        \ (a:path =~# '^\~') ? fnamemodify(a:path, ':p') :
        \ (a:path =~# '^\$\h\w*') ? substitute(a:path,
        \             '^\$\h\w*', '\=eval(submatch(0))', '') :
        \ a:path)
endfunction"}}}

function! denite#util#alternate_buffer() abort
  if len(filter(range(1, bufnr('$')), 'buflisted(v:val)')) <= 1
    enew
    return
  endif

  let cnt = 0
  let pos = 1
  let current = 0
  while pos <= bufnr('$')
    if buflisted(pos)
      if pos == bufnr('%')
        let current = cnt
      endif

      let cnt += 1
    endif

    let pos += 1
  endwhile

  if current > cnt / 2
    bprevious
  else
    bnext
  endif
endfunction
function! denite#util#delete_buffer(command, bufnr) abort
  if index(tabpagebuflist(), a:bufnr) < 0
    silent execute a:bufnr a:command
    return
  endif

  let buffers = filter(range(1, bufnr('$')), 'buflisted(v:val)')
  if len(buffers) == 1 && bufname(buffers[0]) ==# ''
    " Noname buffer only
    return
  endif

  " Not to close window, move to alternate buffer.
  let prev_winnr = winnr()
  for winnr in range(1, winnr('$'))
    if winbufnr(winnr) == a:bufnr
      execute winnr . 'wincmd w'
      call denite#util#alternate_buffer()
    endif
  endfor
  execute prev_winnr . 'wincmd w'
  silent execute a:bufnr a:command
endfunction

function! denite#util#input_yesno(message) abort
  let yesno = input(a:message . ' [yes/no]: ')
  while yesno !~? '^\%(y\%[es]\|n\%[o]\)$'
    redraw
    if yesno ==# ''
      echo 'Canceled.'
      break
    endif

    " Retry.
    call denite#util#print_error('Invalid input.')
    let yesno = input(a:message . ' [yes/no]: ')
  endwhile

  redraw

  return yesno =~? 'y\%[es]'
endfunction
