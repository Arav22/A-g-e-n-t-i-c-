"""Application service wiring API models to orchestrator."""

from __future__ import annotations

from agentic_ai.api.models import TaskRequest, TaskResponse
from agentic_ai.orchestrator.core import Orchestrator


class AgentService:
    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orchestrator = orchestrator

    def run_task(self, request: TaskRequest) -> TaskResponse:
        output = self.orchestrator.run(request.prompt)
        return TaskResponse(output=output)
