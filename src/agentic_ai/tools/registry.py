from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


ToolHandler = Callable[[str, dict[str, Any]], str]


@dataclass(slots=True)
class ToolRegistry:
    _tools: dict[str, ToolHandler] = field(default_factory=dict)

    def register(self, name: str, handler: ToolHandler) -> None:
        self._tools[name] = handler

    def run(self, name: str, prompt: str, context: dict[str, Any] | None = None) -> str:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        return self._tools[name](prompt, context or {})

    def available(self) -> list[str]:
        return sorted(self._tools.keys())


def default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    def reasoning_tool(prompt: str, context: dict[str, Any]) -> str:
        objective = context.get("objective", "")
        return f"Reasoned action for '{prompt}' under objective '{objective}'."

    def search_tool(prompt: str, context: dict[str, Any]) -> str:
        return f"Search findings synthesized for: {prompt}"

    registry.register("reason", reasoning_tool)
    registry.register("search", search_tool)
    return registry
