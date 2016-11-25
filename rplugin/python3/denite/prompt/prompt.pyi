import enum
from datetime import timedelta
from typing import Optional, Union, Tuple, NamedTuple
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


Condition = NamedTuple('Condition', [
    ('text', str),
    ('caret_locus', int),
])


class Prompt:
    """Prompt class."""

    prefix = ...  # type: str

    highlight_prefix = ...  # type: str

    highlight_text = ...  # type: str

    highlight_caret = ...  # type: str

    def __init__(self, nvim: Nvim) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, value: str) -> None: ...

    def insert_text(self, text: str) -> None: ...

    def replace_text(self, text: str) -> None: ...

    def update_text(self, text: str) -> None: ...

    def redraw_prompt(self) -> None: ...

    def start(self) -> Status: ...

    def on_init(self) -> Optional[Status]: ...

    def on_update(self, status: Status) -> Optional[Status]: ...

    def on_redraw(self) -> None: ...

    def on_keypress(self, keystroke: Keystroke) -> Optional[Status]: ...

    def on_term(self, status: Status) -> Status: ...

    def store(self) -> Condition: ...

    def restore(self, condition: Condition) -> None: ...
