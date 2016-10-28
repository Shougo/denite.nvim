class Context:
    text = ... # type: str
    caret_locus = ... # type: int

    def to_dict(self) -> dict: ...

    def extend(self, d: dict) -> None: ...

    @classmethod
    def from_dict(cls, d: dict) -> Context: ...
