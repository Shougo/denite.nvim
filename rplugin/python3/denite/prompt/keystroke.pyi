from typing import cast, Union, Tuple, Iterable
from neovim import Nvim
from .key import Key


KeystrokeType = Tuple[Key, ...]

KeystrokeExpr = Union[KeystrokeType, bytes, str]


class Keystroke(tuple):
    __slots__ = ()  # type: Tuple[str, ...]

    def startswith(self, other: Keystroke) -> bool: ...

    @classmethod
    def parse(cls, nvim: Nvim, expr: KeystrokeExpr) -> Keystroke: ...


def _ensure_keys(nvim: Nvim, expr: KeystrokeExpr) -> KeystrokeType: ...
