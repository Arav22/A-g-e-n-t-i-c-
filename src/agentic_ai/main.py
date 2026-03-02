"""CLI entrypoint for the agentic ai scaffold."""

from __future__ import annotations

import argparse

from agentic_ai.api.models import TaskRequest
from agentic_ai.api.service import AgentService
from agentic_ai.memory.store import MemoryStore
from agentic_ai.observability.logging import configure_logging
from agentic_ai.orchestrator.core import Orchestrator
from agentic_ai.providers.simple_provider import SimpleProvider
from agentic_ai.tools.registry import ToolRegistry
from agentic_ai.tools.word_count import word_count


def build_service() -> AgentService:
    memory = MemoryStore()
    tools = ToolRegistry()
    tools.register("word_count", word_count)
    provider = SimpleProvider()
    orchestrator = Orchestrator(memory=memory, tools=tools, provider=provider)
    return AgentService(orchestrator=orchestrator)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agentic AI scaffold CLI")
    parser.add_argument("--prompt", required=True, help="Prompt for the agentic workflow")
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    service = build_service()
    response = service.run_task(TaskRequest(prompt=args.prompt))
    print(response.output)
    return 0
