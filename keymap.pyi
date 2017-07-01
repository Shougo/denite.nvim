from datetime import datetime, timedelta
from typing import (  # noqa: F401
    Iterator, Optional, Sequence, Tuple, Union, NamedTuple,
    Callable, Dict
)
from neovim import Nvim
from .key import KeyCode
from .keystroke import Keystroke, KeystrokeExpr


Rule = Union[
    Tuple[KeystrokeExpr, KeystrokeExpr],
    Tuple[KeystrokeExpr, KeystrokeExpr, str],
]

DefinitionBase = NamedTuple('DefinitionBase', [
    ('lhs', Keystroke),
    ('rhs', Keystroke),
    ('noremap', bool),
    ('nowait', bool),
    ('expr', bool),
])


class Definition(DefinitionBase):

    @classmethod
    def parse(cls, nvim: Nvim, rule: Rule) -> 'Definition': ...


class Keymap:
    registry = ...  # type: Dict[Keystroke, Definition]

    def clear(self) -> None: ...

    def register(self, definition: Definition) -> None: ...

    def register_from_rule(self, nvim: Nvim, rule: Rule) -> None: ...

    def register_from_rules(self,
                            nvim: Nvim,
                            rules: Sequence[Rule]) -> None: ...

    def filter(self, lhs: Keystroke) -> Iterator[Definition]: ...

    def resolve(self,
                nvim: Nvim,
                lhs: Keystroke,
                nowait: bool=False) -> Optional[Keystroke]: ...

    def harvest(self, nvim: Nvim,
                timeoutlen: Optional[timedelta],
                callback: Optional[Callable],
                interval: float=0.033) -> Keystroke: ...

    @classmethod
    def from_rules(cls, nvim: Nvim, rules: Sequence[Rule]) -> 'Keymap': ...


def _getcode(nvim: Nvim,
             timeout: Optional[datetime],
             callback: Optional[Callable],
             interval: float) -> Optional[KeyCode]: ...
