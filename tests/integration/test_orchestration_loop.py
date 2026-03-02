from agentic.executor import Executor
from agentic.orchestrator import Orchestrator
from agentic.planner import Planner
from agentic.tool_adapters import EchoTool, ToolRegistry


def test_full_objective_runs_through_orchestration_loop() -> None:
    orchestrator = Orchestrator(
        planner=Planner(),
        executor=Executor(ToolRegistry([EchoTool()])),
    )

    result = orchestrator.run_objective("Prepare release notes")

    assert result.plan.objective == "Prepare release notes"
    assert len(result.plan.steps) == 4
    assert result.execution.used_tool == "echo"
    assert result.execution.outputs[-1] == "echo:Summarize outcome"
