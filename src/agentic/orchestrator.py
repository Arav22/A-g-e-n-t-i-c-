from __future__ import annotations

from dataclasses import dataclass

from .executor import ExecutionResult, Executor
from .planner import Plan, Planner


@dataclass(frozen=True)
class OrchestrationResult:
    plan: Plan
    execution: ExecutionResult


class Orchestrator:
    """Coordinates objective -> plan -> execution loop."""

    def __init__(self, planner: Planner, executor: Executor) -> None:
        self._planner = planner
        self._executor = executor

    def run_objective(self, objective: str) -> OrchestrationResult:
        plan = self._planner.create_plan(objective)
        execution = self._executor.execute(plan)
        return OrchestrationResult(plan=plan, execution=execution)
