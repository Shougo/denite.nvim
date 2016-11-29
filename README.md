neovim-prompt
===============================================================================
[![Travis CI](https://img.shields.io/travis/lambdalisue/neovim-prompt/master.svg?style=flat-square&label=Travis%20CI)](https://travis-ci.org/lambdalisue/neovim-prompt)
[![Coverage Status](https://coveralls.io/repos/github/lambdalisue/neovim-prompt/badge.svg?branch=master)](https://coveralls.io/github/lambdalisue/neovim-prompt?branch=master)
[![Code Quality](https://img.shields.io/scrutinizer/g/lambdalisue/neovim-prompt/master.svg)](https://scrutinizer-ci.com/g/lambdalisue/neovim-prompt/?branch=master)
![Version 1.0.0](https://img.shields.io/badge/version-1.0.0-yellow.svg?style=flat-square)
![Support Neovim 0.1.6 or above](https://img.shields.io/badge/support-Neovim%200.1.6%20or%20above-green.svg?style=flat-square)
![Support Vim 8.0 or above](https://img.shields.io/badge/support-Vim%208.0.0%20or%20above-yellowgreen.svg?style=flat-square)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE.md)
[![Documentation Status](https://readthedocs.org/projects/neovim-prompt/badge/?version=latest)](http://neovim-prompt.readthedocs.io/en/latest/?badge=latest)


A customizable command-line prompt module for Neovim/Vim.
This repository is assumed to used as a submodule/subtree package.


Usage
-------------------------------------------------------------------------------

Assume you are 'PETER' and you are making 'my-awesome-vim-plugin'.

### git submodule

If you won't touch the code in neovim-prompt, this is a best way to use neovim-prompt in your plugin.

```sh
git clone https://github.com/PETER/my-awesome-vim-plugin
cd my-awesome-vim-plugin
git submodule add https://github.com/lambdalisue/neovim-prompt rplugin/python3/my_awesome_vim_plugin/prompt
```

### git subtree

It is complicated so if you are not really familiar with git subtree, you should use git submodule instead.

First of all, fork https://github.com/lambdalisue/neovim-prompt to GitHub.
Then clone your neovim-prompt to the same parent directory to the your plugin like

```sh
git clone https://github.com/PETER/my-awesome-vim-plugin
git clone https://github.com/PETER/neovim-prompt
```

Then, add cloned local repository as a remote repository of 'my-awesome-vim-plugin' like

```sh
cd my-awesome-vim-plugin
git remote add neovim-prompt ../neovim-prompt
```

Then perform the following. Note that following is used for update neovim-prompt to the latest as well.

```sh
git fetch neovim-prompt
git subtree pull --prefix=rplugin/python3/my_awesome_vim_plugin/prompt neovim-prompt master --squash
```

When you change the neovim-prompt code and you think it's valuable for other peoples, make a PR with

```sh
git fetch neovim-prompt
git subtree push --prefix=rplugin/python3/my_awesome_vim_plugin/prompt neovim-prompt some-awesome-implementation --squash
cd ../neovim-prompt
git checkout some-awesome-implementation
git push -u origin
```

Then send me a PR. I'll check the implementations and concepts.
Please try to make clear commits before sending me a PR.


### Python code

If you followed the above, you can use neovim-prompt as like the following.

```python3
from .prompt.prompt import (
    Prompt,
    STATUS_ACCEPT,
    STATUS_CANCEL,
    STATUS_INTERRUPT,
)

# ...

    prompt = Prompt()
    status = prompt.start()
    if status == STATUS_ACCEPT:
        result = prompt.text
        # Do what ever you want
    elif status == STATUS_CANCEL:
        # User hit <Esc> (or whatever which is mapped to <prompt:cancel>)
    elif status == STATUS_INTERRUPT:
        # User hit <C-c> to interrupt

# ...
```

See [API document](http://neovim-prompt.readthedocs.io/en/latest/?badge=latest) or real world examples for more detail.


Tests
----------------------------------------------------------

While neovim-prompt is assumed to be used as a git submodule/subtree, the 'master' branch does not contain any code for testing but 'ci-test' branch.

First of all, clone 'ci-test' branch of neovim-prompt in neovim-prompt repository as

```sh
git clone https://github.com/lambdalisue/neovim-prompt
cd neovim-prompt
git clone https://github.com/lambdalisue/neovim-prompt --branch ci-test ci-test
```

Then cd to 'ci-test' and run `scripts/test.sh` to perform tests.

```sh
cd ci-test
./scripts/test.sh
```

If you implement features, do not forget to add tests in ci-test branch.


Builtin actions
----------------------------------------------------------

neovim-prompt provides the following builtin actions.

Name | Description
---- | -----------
`<prompt:accept>` | Accept the input and return `STATUS_ACCEPT`.
`<prompt:cancel>` | Cancel the input and return `STATUS_CANCEL`.
`<prompt:toggle_insert_mode>` | Toggle insert mode (insert/overstrike)
`<prompt:delete_char_before_caret>` | Delete a character before the caret
`<prompt:delete_word_before_caret>` | Delete a word before the caret (respect `iskeyword` in Vim)
`<prompt:delete_char_after_caret>` | Delete a character after the caret
`<prompt:delete_word_after_caret>` | Delete a word after the caret (respect `iskeyword` in Vim)
`<prompt:delete_char_under_caret>` | Delete a character under the caret
`<prompt:delete_word_under_caret>` | Delete a word under the caret (respect `iskeyword` in Vim)
`<prompt:delete_text_before_caret>` | Delete test before the caret
`<prompt:delete_text_after_caret>` | Delete test after the caret
`<prompt:delete_entire_text>` | Delete entire text
`<prompt:move_caret_to_left>` | Move the caret to one character left
`<prompt:move_caret_to_one_word_left>` | Move the caret to one word left
`<prompt:move_caret_to_left_anchor>` | Move the caret like `F` in Vim's normal mode
`<prompt:move_caret_to_right>` | Move the caret to one character right
`<prompt:move_caret_to_one_word_right>` | Move the caret to one word right
`<prompt:move_caret_to_right_anchor>` | Move the caret like `f` in Vim's normal mode
`<prompt:move_caret_to_head>` | Move the caret to the head
`<prompt:move_caret_to_lead>` | Move the caret to the start of the printable character
`<prompt:move_caret_to_tail>` | Move the caret to the tail
`<prompt:assign_previous_text>` | Recall previous command-line from history
`<prompt:assign_next_text>` | Recall next command-line from history
`<prompt:assign_previous_matched_text>` | Recall previous command-line from history that matches pattern in front of the caret
`<prompt:assign_next_matched_text>` | Recall next command-line from history that matches pattern in front of the caret
`<prompt:paste_from_register>` | Paste text from a specified register
`<prompt:paste_from_default_register>` | Paste text from `v:register`
`<prompt:yank_to_register>` | Copy text to a specified register
`<prompt:yank_to_default_register>` | Copy text to `v:register`
`<prompt:insert_special>` | Specify and insert a special character (e.g. `^V`, `^M`)
`<prompt:insert_digraph>` | Specify and insert a digraph character (See `:help digraph`)

The above actions are defined in [action.py](./action.py)

Default mappings
----------------------------------------------------------

The default mapping is determined from a Vim's native command-line (`:help ex-edit-index`.)

Key | Action | Params
---- | ----------- | -----
`<C-B>` | `<prompt:move_caret_to_head>` | `noremap`
`<C-E>` | `<prompt:move_caret_to_tail>` | `noremap`
`<BS>` | `<prompt:delete_char_before_caret>` | `noremap`
`<C-H>` | `<prompt:delete_char_before_caret>` | `noremap`
`<S-TAB>` | `<prompt:assign_previous_text>` | `noremap`
`<C-J>` | `<prompt:accept>` | `noremap`
`<C-K>` | `<prompt:insert_digraph>` | `noremap`
`<CR>` | `<prompt:accept>` | `noremap`
`<C-M>` | `<prompt:accept>` | `noremap`
`<C-N>` | `<prompt:assign_next_text>` | `noremap`
`<C-P>` | `<prompt:assign_previous_text>` | `noremap`
`<C-Q>` | `<prompt:insert_special>` | `noremap`
`<C-R>` | `<prompt:paste_from_register>` | `noremap`
`<C-U>` | `<prompt:delete_entire_text>` | `noremap`
`<C-V>` | `<prompt:insert_special>` | `noremap`
`<C-W>` | `<prompt:delete_word_before_caret>` | `noremap`
`<ESC>` | `<prompt:cancel>` | `noremap`
`<DEL>` | `<prompt:delete_char_under_caret>` | `noremap`
`<Left>` | `<prompt:move_caret_to_left>` | `noremap`
`<S-Left>` | `<prompt:move_caret_to_one_word_left>` | `noremap`
`<C-Left>` | `<prompt:move_caret_to_one_word_left>` | `noremap`
`<Right>` | `<prompt:move_caret_to_right>` | `noremap`
`<S-Right>` | `<prompt:move_caret_to_one_word_right>` | `noremap`
`<C-Right>` | `<prompt:move_caret_to_one_word_right>` | `noremap`
`<Up>` | `<prompt:assign_previous_matched_text>` | `noremap`
`<S-Up>` | `<prompt:assign_previous_text>` | `noremap`
`<Down>` | `<prompt:assign_next_matched_text>` | `noremap`
`<S-Down>` | `<prompt:assign_next_text>` | `noremap`
`<Home>` | `<prompt:move_caret_to_head>` | `noremap`
`<End>` | `<prompt:move_caret_to_tail>` | `noremap`
`<PageDown>` | `<prompt:assign_next_text>` | `noremap`
`<PageUp>` | `<prompt:assign_previous_text>` | `noremap`
`<INSERT>` | `<prompt:toggle_insert_mode>` | `noremap`

The above actions are defined in [keymap.py](./kaymap.py)

Plugins which use neovim-prompt
----------------------------------------------------------

- [lambdalisue/lista.nvim](https://github.com/lambdalisue/lista.nvim)
- [Shougo/denite.nvim](https://github.com/Shougo/denite.nvim)
