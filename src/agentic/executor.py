from __future__ import annotations

from dataclasses import dataclass

from .planner import Plan
from .tool_adapters import ToolRegistry


@dataclass(frozen=True)
class ExecutionResult:
    objective: str
    used_tool: str
    outputs: list[str]


class Executor:
    """Runs a plan using a selected tool adapter."""

    def __init__(self, tools: ToolRegistry, default_tool: str = "echo") -> None:
        self._tools = tools
        self._default_tool = default_tool

    def execute(self, plan: Plan) -> ExecutionResult:
        tool = self._tools.get(self._default_tool)
        outputs = [tool.run(step) for step in plan.steps]
        return ExecutionResult(objective=plan.objective, used_tool=tool.name, outputs=outputs)
