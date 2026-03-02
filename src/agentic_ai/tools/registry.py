"""Tool registration and execution primitives."""

from __future__ import annotations

from collections.abc import Callable

ToolFn = Callable[[str], str]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolFn] = {}

    def register(self, name: str, tool_fn: ToolFn) -> None:
        self._tools[name] = tool_fn

    def execute(self, name: str, payload: str) -> str:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        return self._tools[name](payload)

    def has(self, name: str) -> bool:
        return name in self._tools
