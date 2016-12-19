install: vim-themis

	pip install neovim --upgrade
	pip install pytest --upgrade
	pip install flake8 --upgrade
	pip install mypy-lang --upgrade
	pip install vim-vint --upgrade

lint:
	vint --version
	vint plugin
	vint autoload
	flake8 --version
	flake8 rplugin/python3/denite
	mypy --version
	mypy --silent-imports rplugin/python3/denite

test:
	./vim-themis/bin/themis --version
	THEMIS_VIM="nvim" THEMIS_ARGS="-e -s --headless" ./vim-themis/bin/themis test/autoload/*
	pytest --version
	pytest rplugin/python3/denite

vim-themis:
	git clone https://github.com/thinca/vim-themis vim-themis; \


.PHONY: install lint test
