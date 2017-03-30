from neovim import Nvim
from .util import Singleton


class Digraph(metaclass=Singleton):
    registry = ... # type: Dict[str, str]

    def find(self, nvim: Nvim, char1: str, char2: str) -> str: ...

    def retrieve(self, nvim: Nvim) -> str: ...
