"""Orchestrator coordinates prompt -> tool -> provider flow."""

from __future__ import annotations

import logging

from agentic_ai.memory.store import MemoryStore
from agentic_ai.providers.simple_provider import SimpleProvider
from agentic_ai.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self, memory: MemoryStore, tools: ToolRegistry, provider: SimpleProvider) -> None:
        self.memory = memory
        self.tools = tools
        self.provider = provider

    def run(self, prompt: str) -> str:
        logger.info("Received prompt")
        self.memory.add_turn("user", prompt)

        tool_name = "word_count"
        payload = self._extract_payload(prompt)
        logger.info("Executing tool: %s", tool_name)
        tool_result = self.tools.execute(tool_name, payload)
        self.memory.add_turn("tool", f"{tool_name} -> {tool_result}")

        response = self.provider.compose_response(prompt, tool_result, self.memory.history())
        self.memory.add_turn("assistant", response)
        return response

    @staticmethod
    def _extract_payload(prompt: str) -> str:
        marker = "count words in:"
        lowered = prompt.lower()
        if marker in lowered:
            start = lowered.index(marker) + len(marker)
            return prompt[start:].strip()
        return prompt
