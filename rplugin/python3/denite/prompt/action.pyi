import re  # noqa: F401
from typing import (  # noqa: F401
    Callable, Optional, Dict, Tuple, Sequence, Pattern
)
from .prompt import Prompt

ACTION_PATTERN = ...  # type: Pattern

ActionCallback = Callable[[Prompt, str], Optional[int]]
ActionRules = Sequence[Tuple[str, ActionCallback]]


class Action:
    registry = ...  # type: Dict[str, ActionCallback]

    def clear(self) -> None: ...

    def register(self, name: str, callback: ActionCallback) -> None: ...

    def register_from_rules(self, rules: ActionRules) -> None: ...

    def call(self, prompt: Prompt, name: str) -> Optional[int]: ...

    @classmethod
    def from_rules(cls, rules: ActionRules) -> 'Action': ...


DEFAULT_ACTION = ...  # type: Action
