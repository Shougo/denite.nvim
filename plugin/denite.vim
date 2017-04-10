"=============================================================================
" FILE: denite.vim
" AUTHOR:  Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

if exists('g:loaded_denite')
  finish
endif
let g:loaded_denite = 1

command! -nargs=+ -range -complete=customlist,denite#helper#complete
      \ Denite
      \ call denite#helper#call_denite('Denite',
      \                                <q-args>, <line1>, <line2>)
command! -nargs=+ -range -complete=customlist,denite#helper#complete
      \ DeniteCursorWord
      \ call denite#helper#call_denite('DeniteCursorWord',
      \                                <q-args>, <line1>, <line2>)
command! -nargs=+ -range -complete=customlist,denite#helper#complete
      \ DeniteBufferDir
      \ call denite#helper#call_denite('DeniteBufferDir',
      \                                <q-args>, <line1>, <line2>)
command! -nargs=+ -range -complete=customlist,denite#helper#complete
      \ DeniteProjectDir
      \ call denite#helper#call_denite('DeniteProjectDir',
      \                                <q-args>, <line1>, <line2>)
