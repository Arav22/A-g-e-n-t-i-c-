from __future__ import annotations

from dataclasses import asdict
from typing import Any

from agentic_ai.orchestrator.engine import OrchestrationEngine
from agentic_ai.orchestrator.state import RunStateStore


class OrchestratorAPI:
    def __init__(self, run_dir: str = ".runs") -> None:
        self.engine = OrchestrationEngine(store=RunStateStore(run_dir))

    def run(self, objective: str) -> dict[str, Any]:
        state = self.engine.start(objective)
        return asdict(state)

    def resume(self, run_id: str) -> dict[str, Any]:
        state = self.engine.resume(run_id)
        return asdict(state)
