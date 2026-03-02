"""Provider abstraction for forming final responses."""

from __future__ import annotations

from agentic_ai.memory.store import Turn


class SimpleProvider:
    """A tiny provider stub that composes a final response."""

    def compose_response(self, prompt: str, tool_result: str, history: list[Turn]) -> str:
        history_len = len(history)
        return (
            "Task complete. "
            f"Prompt='{prompt}'. "
            f"Tool output: {tool_result}. "
            f"Conversation turns stored: {history_len}."
        )
