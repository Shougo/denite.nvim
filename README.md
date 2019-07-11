denite.nvim
===========

[![Build Status](https://travis-ci.org/Shougo/denite.nvim.svg?branch=master)](https://travis-ci.org/Shougo/denite.nvim)

Note: Denite.nvim does not define any of default mappings.  You need to define
them.


## About

[![Join the chat at https://gitter.im/Shougo/denite.nvim](https://badges.gitter.im/Shougo/denite.nvim.svg)](https://gitter.im/Shougo/denite.nvim?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Denite is a dark powered plugin for Neovim/Vim to unite all interfaces.
It can replace many features or plugins with its interface.
It is like a fuzzy finder, but is more generic.
You can extend the interface and create the sources.

Some things you can do with it include:

* Opening files

* Switching buffers

* Inserting the value of a register

* Changing current directory

* Searching for a string

[Unite.vim](https://github.com/Shougo/unite.vim) was meant to be like [Helm](https://github.com/emacs-helm/helm) for Vim.
But the implementation is ugly and it's very slow.

Denite resolves Unite's problems. Here are some of its benefits:

* Theoretically faster because the main process is executed by Python

* Theoretically more stable because no other processes can be performed when
it runs.

* The implementation is simpler than unite

* Has greater potential to implement new features

* Python3 is easier to work with than Vimscript

* There are a lot of useful tools to keep code simple (linter, tester, etc...)
in Python3.

* Unite is officially obsolete, minor bugs (or even major bugs) are
not fixed anymore


## Requirements

Denite requires Neovim 0.3.0+ or Vim 8.0+ with `if_python3`.
If `:echo has("python3")` returns `1`, then you're done.

Note: You need to install Python3.6.1+.

For neovim:

You must install "pynvim" module with pip

    pip3 install --user pynvim

If you want to read the Neovim-python/python3 interface install documentation,
you should read `:help provider-python`.

For Vim8:

Please install nvim-yarp plugin for Vim8.
https://github.com/roxma/nvim-yarp

Please install vim-hug-neovim-rpc plugin for Vim8.
https://github.com/roxma/vim-hug-neovim-rpc

You must install "pynvim" module with pip

    pip3 install --user pynvim


### For Windows users

1. Install Vim from [Vim Win32 Installer
   releases](https://github.com/vim/vim-win32-installer/releases)
2. Download [Python latest embeddable zip
   file](https://www.python.org/downloads/windows/) and copy the all files in
   the zip file to the folder where you installed Vim.

**Note:** You need to do 1. and 2. with the common-arch files (x86 or x64).


## Examples

```vim
" Define mappings
autocmd FileType denite call s:denite_my_settings()
function! s:denite_my_settings() abort
  nnoremap <silent><buffer><expr> <CR>
  \ denite#do_map('do_action')
  nnoremap <silent><buffer><expr> d
  \ denite#do_map('do_action', 'delete')
  nnoremap <silent><buffer><expr> p
  \ denite#do_map('do_action', 'preview')
  nnoremap <silent><buffer><expr> q
  \ denite#do_map('quit')
  nnoremap <silent><buffer><expr> i
  \ denite#do_map('open_filter_buffer')
  nnoremap <silent><buffer><expr> <Space>
  \ denite#do_map('toggle_select').'j'
endfunction
```


## Screenshots

![denite new UI](https://user-images.githubusercontent.com/1239245/58742567-a155ea80-8460-11e9-9925-09082def2c80.gif)
![denite new UI2](https://user-images.githubusercontent.com/41671631/58790351-cf832800-8622-11e9-912d-813408876b86.gif)
