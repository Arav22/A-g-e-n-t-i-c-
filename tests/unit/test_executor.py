from agentic.executor import Executor
from agentic.planner import Plan
from agentic.tool_adapters import EchoTool, ToolRegistry


def test_executor_runs_all_plan_steps_with_default_tool() -> None:
    executor = Executor(ToolRegistry([EchoTool()]))
    plan = Plan(objective="Deliver", steps=["step1", "step2"])

    result = executor.execute(plan)

    assert result.objective == "Deliver"
    assert result.used_tool == "echo"
    assert result.outputs == ["echo:step1", "echo:step2"]
