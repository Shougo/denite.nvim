## About

[![Join the chat at https://gitter.im/Shougo/denite.nvim](https://badges.gitter.im/Shougo/denite.nvim.svg)](https://gitter.im/Shougo/denite.nvim?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Denite.nvim is a dark powered Neovim unite all interfaces.

Note: This is the my next vaporware!


## Test method

    Denite file_rec


## Requirements

denite requires Neovim with if\_python3.
If `:echo has("python3")` returns `1`, then you're done; otherwise, see below.

You can enable Python3 interface with pip:

    pip3 install neovim

If you want to read the Neovim-python/python3 interface install documentation,
you should read `:help provider-python`.


## Future works (not implemented yet)

* Implement some sources (grep, line)

* Can call unite sources

