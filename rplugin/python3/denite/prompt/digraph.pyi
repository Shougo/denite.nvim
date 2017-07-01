from neovim import Nvim
from .util import Singleton
from typing import Dict  # noqa: F401


class Digraph(metaclass=Singleton):
    registry = ...  # type: Dict[str, str]

    def find(self, nvim: Nvim, char1: str, char2: str) -> str: ...

    def retrieve(self, nvim: Nvim) -> str: ...
