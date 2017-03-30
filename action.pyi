from typing import Callable, Optional, Dict, Tuple, Sequence
from .prompt import Prompt, Status


ActionCallback = Callable[[Prompt, str], Optional[Status]]
ActionRules = Sequence[Tuple[str, ActionCallback]]


class Action:
    registry = ... # type: Dict[str, ActionCallback]

    def clear(self) -> None: ...

    def register(self, name: str, callback: ActionCallback) -> None: ...

    def register_from_rules(self, rules: ActionRules) -> None: ...

    def call(self, prompt: Prompt, name: str) -> Optional[Status]: ...

    @classmethod
    def from_rules(cls, rules: ActionRules) -> Action: ...
