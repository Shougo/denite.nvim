test: vim-themis
	# ./vim-themis/bin/themis --reporter spec test
	nosetests -v rplugin/python3
	flake8 rplugin/ --exclude rplugin/python3/denite/prompt/docs/conf.py

# Use existing vim-themis install from ~/.vim, or clone it.
vim-themis:
	git clone https://github.com/thinca/vim-themis vim-themis; \

.PHONY: test
