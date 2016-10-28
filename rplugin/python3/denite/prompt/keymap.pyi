from datetime import datetime
from typing import Iterator, Optional, Sequence, Tuple, Union
from neovim import Nvim
from .key import KeyCode
from .keystroke import Keystroke, KeystrokeExpr


RuleDef = Tuple[KeystrokeExpr, KeystrokeExpr, bool, bool]
Rule = Union[
    Tuple[KeystrokeExpr, KeystrokeExpr],
    Tuple[KeystrokeExpr, KeystrokeExpr, bool],
    RuleDef,
]


class Keymap:
    registry = ...  # type: Dict[Keystroke, RuleDef]

    def register(self,
                 lhs: Keystroke,
                 rhs: Keystroke,
                 noremap: bool=False,
                 nowait: bool=False) -> None: ...

    def register_from_rule(self, nvim: Nvim, rule: Rule) -> None: ...

    def register_from_rules(self,
                            nvim: Nvim,
                            rules: Sequence[Rule]) -> None: ...

    def filter(self, lhs: Keystroke) -> Iterator[Keystroke]: ...

    def resolve(self,
                lhs: Keystroke,
                nowait: bool=False) -> Optional[Keystroke]: ...

    def harvest(self, nvim: Nvim,
                timeoutlen: Optional[int]=None) -> Keystroke: ...

    @classmethod
    def from_rules(cls, nvim: Nvim, rules: Sequence[Rule]) -> Keymap: ...


def _getcode(nvim: Nvim,
             timeout: Optional[datetime]) -> Optional[KeyCode]: ...
