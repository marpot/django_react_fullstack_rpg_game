from collections.abc import Mapping
from dataclasses import dataclass


ALLOWED_ACTIONS = frozenset({
    "attack", "move", "inspect", "talk", "defend", "use_item",
})


@dataclass(frozen=True)
class GameCommand:
    action: str
    target: str | None = None
    method: str | None = None

    def __post_init__(self):
        if not isinstance(self.action, str) or self.action not in ALLOWED_ACTIONS:
            raise ValueError("invalid_action")
        if self.target is not None and not isinstance(self.target, str):
            raise ValueError("invalid_target")
        if self.method is not None and not isinstance(self.method, str):
            raise ValueError("invalid_method")

    @classmethod
    def from_mapping(cls, value: Mapping) -> "GameCommand":
        if not isinstance(value, Mapping):
            raise ValueError("invalid_command")
        return cls(
            action=value.get("action"),
            target=value.get("target"),
            method=value.get("method"),
        )
