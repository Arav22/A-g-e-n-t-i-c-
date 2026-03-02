"""Tool permission policy for whitelisting actions."""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_ai.errors import PolicyDeniedError


@dataclass(slots=True)
class ToolPermissionPolicy:
    """Allow-list based permission model for tool actions."""

    allowed_actions: dict[str, set[str]] = field(default_factory=dict)

    def is_allowed(self, tool_name: str, action: str) -> bool:
        allowed = self.allowed_actions.get(tool_name)
        if not allowed:
            return False
        return action in allowed

    def enforce(self, tool_name: str, action: str) -> None:
        if not self.is_allowed(tool_name, action):
            raise PolicyDeniedError(tool_name, action)

    @classmethod
    def from_mapping(cls, mapping: dict[str, list[str] | set[str] | tuple[str, ...]]) -> "ToolPermissionPolicy":
        normalized = {name: set(actions) for name, actions in mapping.items()}
        return cls(allowed_actions=normalized)
