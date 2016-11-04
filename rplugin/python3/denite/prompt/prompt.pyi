import enum
from datetime import timedelta
from typing import Optional, Union, Tuple
from neovim import Nvim
from .key import Key
from .keystroke import Keystroke
from .context import Context

KeystrokeType = Tuple[Key, ...]
KeystrokeExpr = Union[KeystrokeType, bytes, str]


class Status(enum.Enum):
    """A prompt status enum class."""

    progress = 0
    accept = 1
    cancel = 2
    error = 3


class InsertMode(enum.Enum):
    """A insert mode enum class."""

    insert = 1
    replace = 2


class Prompt:
    """Prompt class."""

    prefix = ...  # type: str

    def __init__(self, nvim: Nvim, context: Context) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, value: str) -> None: ...

    def apply_custom_mappings_from_vim_variable(self,
                                                varname: str) -> None: ...

    def insert_text(self, text: str) -> None: ...

    def replace_text(self, text: str) -> None: ...

    def update_text(self, text: str) -> None: ...

    def redraw_prompt(self) -> None: ...

    def start(self, default: str=None) -> Status: ...

    def on_init(self, default: Optional[str]) -> Optional[Status]: ...

    def on_update(self, status: Optional[Status]) -> Status: ...

    def on_redraw(self) -> None: ...

    def on_keypress(self, keystroke: Keystroke) -> Optional[Status]: ...

    def on_term(self, status: Status) -> Status: ...


def _build_echon_expr(hl: str, text: str) -> str: ...
