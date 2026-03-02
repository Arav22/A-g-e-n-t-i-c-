import pytest

from agentic.planner import Planner


def test_create_plan_generates_expected_steps() -> None:
    planner = Planner()

    plan = planner.create_plan("Ship release")

    assert plan.objective == "Ship release"
    assert len(plan.steps) == 4
    assert plan.steps[0] == "Clarify objective: Ship release"


def test_create_plan_rejects_empty_objective() -> None:
    planner = Planner()

    with pytest.raises(ValueError, match="Objective must not be empty"):
        planner.create_plan("   ")
