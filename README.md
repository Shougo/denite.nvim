denite.nvim
===========

[![Build Status](https://travis-ci.org/Shougo/denite.nvim.svg?branch=master)](https://travis-ci.org/Shougo/denite.nvim)

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

Denite requires Neovim or Vim8.0+ with `if_python3`.
If `:echo has("python3")` returns `1`, then you're done; otherwise, see below.

You can enable Python3 interface with `pip`:

    pip3 install neovim

If you want to read the Neovim-python/python3 interface install documentation,
you should read `:help provider-python`.

Note: You need to install Python3.5+ or `pip3 install typing`.

### For Windows users

1. Install Vim from [Vim Win32 Installer releases](https://github.com/vim/vim-win32-installer/releases)
2. Download [Python3.5.3 embeddable zip file](https://www.python.org/downloads/release/python-353/) and copy the all files in the zip file to the folder where you installed Vim.

**Note:** You need to do 1. and 2. with the common-arch files (x86 or x64).

## Future works (not implemented yet)

* source completion support: `completion(args, arglead)`

* [`defx`](https://github.com/Shougo/defx.nvim) support

* match highlight improvement

## Screenshots

![file_rec source](https://user-images.githubusercontent.com/13142418/34324674-b8ddd5b8-e840-11e7-9b77-d94e1b084bda.gif)
![SpaceVim Guide](https://user-images.githubusercontent.com/13142418/34324752-e5a89900-e842-11e7-9f87-6d8789ba3871.gif)
![colorscheme source](https://user-images.githubusercontent.com/13142418/34324786-f4dd39a2-e843-11e7-97ef-7a48ee04d27b.gif)

