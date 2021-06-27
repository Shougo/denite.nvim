denite.nvim
===========

**Note**: Active development on denite.nvim has stopped. The only future
changes will be bug fixes.

Please see [ddu.vim](https://github.com/Shougo/ddu.vim).


Note: Denite.nvim does not define any of default mappings.  You need to define
them.

Please read [help](doc/denite.txt) for details.


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

Denite requires Neovim 0.4.0+ or Vim 8.0+ with `if_python3`.
If `:echo has("python3")` returns `1`, then you're done.

Note: Please install/upgrade msgpack package (1.0.0+).
https://github.com/msgpack/msgpack-python

Note: You need to install Python 3.6.1+.

For neovim:

You must install "pynvim" module with pip

    pip3 install --user pynvim

If you want to read the pynvim/python3 interface install documentation,
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


## Installation

For [dein.vim](https://github.com/Shougo/dein.vim)

```
call dein#add('Shougo/denite.nvim')
if !has('nvim')
  call dein#add('roxma/nvim-yarp')
  call dein#add('roxma/vim-hug-neovim-rpc')
endif
```

For [vim-plug](https://github.com/junegunn/vim-plug)

```
if has('nvim')
  Plug 'Shougo/denite.nvim', { 'do': ':UpdateRemotePlugins' }
else
  Plug 'Shougo/denite.nvim'
  Plug 'roxma/nvim-yarp'
  Plug 'roxma/vim-hug-neovim-rpc'
endif
```


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

### Old UI

![denite old UI](https://user-images.githubusercontent.com/13142418/65154984-06107180-da5f-11e9-8cbf-e0a544d0dbc5.jpg)

### New UI

![denite new UI](https://user-images.githubusercontent.com/13142418/65154937-f002b100-da5e-11e9-8aef-723233e3704d.jpg)

### Others

![denite new UI2](https://user-images.githubusercontent.com/1239245/58742567-a155ea80-8460-11e9-9925-09082def2c80.gif)
![denite new UI3](https://user-images.githubusercontent.com/41671631/58790351-cf832800-8622-11e9-912d-813408876b86.gif)
