"=============================================================================
" FILE: project.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

let s:vcs_markers = ['.git', '.bzr', '.hg', '.svn']

function! denite#project#path2project_directory(path, root_markers) abort
  return denite#util#substitute_path_separator(
        \ s:path2project_directory(a:path, a:root_markers))
endfunction

function! s:path2project_directory(path, root_markers) abort
  let search_directory = denite#util#path2directory(a:path)
  let directory = ''

  " Search project root marker file.
  for d in split(a:root_markers, ',')
    let d = findfile(d, s:escape_file_searching(search_directory) . ';')
    if d !=# ''
      return fnamemodify(d, ':p:h')
    endif

    " Allow the directory.
    let d = finddir(d, s:escape_file_searching(search_directory) . ';')
    if d !=# ''
      return fnamemodify(d, ':p')
    endif
  endfor

  " Search VCS directory.
  for vcs in s:vcs_markers
    if vcs ==# '.git'
      let directory = s:_path2project_directory_git(search_directory)
    elseif vcs ==# '.svn'
      let directory = s:_path2project_directory_svn(search_directory)
    else
      let directory = s:_path2project_directory_others(vcs, search_directory)
    endif
    if directory !=# ''
      return directory
    endif
  endfor

  " Search /src/ directory.
  let base = denite#util#substitute_path_separator(search_directory)
  if base =~# '/src/'
    let directory = base[: strridx(base, '/src/') + 3]
  endif

  if directory ==# ''
    " Use original path.
    let directory = search_directory
  endif

  return directory
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
  let parent_directory = denite#util#path2directory(
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
