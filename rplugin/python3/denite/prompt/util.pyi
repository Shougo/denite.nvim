from typing import Any, AnyStr, Union
from neovim import Nvim


def get_encoding(nvim: Nvim) -> str: ...


def ensure_bytes(nvim: Nvim, seed: AnyStr) -> bytes: ...


def ensure_str(nvim: Nvim, seed: AnyStr) -> str: ...


def int2char(nvim: Nvim, code: int) -> str: ...


def int2repr(nvim: Nvim, code: Union[int, bytes]) -> str: ...


def getchar(nvim: Nvim, *args) -> Union[int, bytes]: ...


def build_echon_expr(text: str, hl: str) -> str: ...


class Singleton(type):
    instance = ...  # tyoe: object
