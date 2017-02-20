## About

[![Join the chat at https://gitter.im/Shougo/denite.nvim](https://badges.gitter.im/Shougo/denite.nvim.svg)](https://gitter.im/Shougo/denite.nvim?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Denite.nvim is a dark powered for Neovim/Vim unite all interfaces.
It can replace many features or plugins by the interface.
It is like the fuzzy finder, but it is more generic.
You can extend the interface by the customization and to create the sources.

* Open the files

* Switch buffers

* Insert the register value

* Change the current directory

* Search the candidates

Unite.vim is anything.el like interface for Vim.
But the implementation is ugly and very slow.
Denite.nvim resolves unite.vim problems.
It is 10 times faster than unite.vim.

* Theoretically faster while the main process is executed by python

* Theoretically more stable while no other processes can be performed when
denite.nvim is executed.

* The implementation is relatively simple than unite.vim

* Denite.nvim has great potential to implement a new feature

* To send the pull request by Python3 is easier than Vim script

* There are a lot of useful tools to keep code simple (linter, tester, etc...)
in Python3.

* The unite.vim is officially obsolete, minor bugs (or even major bugs) are
not fixed anymore


## Requirements

denite requires Neovim or Vim8.0+ with if\_python3.
If `:echo has("python3")` returns `1`, then you're done; otherwise, see below.

You can enable Python3 interface with pip:

    pip3 install neovim

If you want to read the Neovim-python/python3 interface install documentation,
you should read `:help provider-python`.


## Future works (not implemented yet)

* source completion support: completion(args, arglead)

* matcher_hide_hidden_files

* quickmatch feature

* file and file:new source

* -no-split, -tab option

* tag and tag:include source

* defx.nvim support

* match highlight improvement

* denite#custom#action()
