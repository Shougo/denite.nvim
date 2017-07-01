from typing import Union, Tuple, Dict, NamedTuple
from neovim import Nvim


KeyCode = Union[int, bytes]
KeyExpr = Union[KeyCode, str]

KeyBase = NamedTuple('KeyBase', [
    ('code', KeyCode),
    ('char', str),
])


class Key(KeyBase):

    __slots__ = ()  # type: Tuple[str, ...]
    __cached = {}   # type: Dict[KeyExpr, Key]

    @classmethod
    def represent(cls, nvim: Nvim, code: KeyCode) -> str: ...

    @classmethod
    def parse(cls, nvim: Nvim, expr: KeyExpr) -> Key: ...


def _resolve(nvim: Nvim, expr: KeyExpr) -> KeyCode: ...


def _resolve_from_special_keys(nvim: Nvim, inner: bytes) -> KeyCode: ...
