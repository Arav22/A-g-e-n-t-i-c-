"""Simple memory layer storing conversation turns."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Turn:
    role: str
    content: str


class MemoryStore:
    def __init__(self) -> None:
        self._turns: list[Turn] = []

    def add_turn(self, role: str, content: str) -> None:
        self._turns.append(Turn(role=role, content=content))

    def history(self) -> list[Turn]:
        return list(self._turns)
