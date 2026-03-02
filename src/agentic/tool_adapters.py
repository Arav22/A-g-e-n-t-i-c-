from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ToolAdapter(Protocol):
    name: str

    def run(self, instruction: str) -> str:
        """Execute an instruction and return textual output."""


@dataclass
class EchoTool:
    name: str = "echo"

    def run(self, instruction: str) -> str:
        return f"echo:{instruction}"


class ToolRegistry:
    def __init__(self, adapters: list[ToolAdapter]) -> None:
        if not adapters:
            raise ValueError("At least one tool adapter is required")
        self._adapters = {adapter.name: adapter for adapter in adapters}

    def names(self) -> list[str]:
        return sorted(self._adapters.keys())

    def get(self, name: str) -> ToolAdapter:
        try:
            return self._adapters[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool adapter '{name}'") from exc
