from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    objective: str
    steps: list[str]


class Planner:
    """Builds a deterministic plan from a plain-language objective."""

    def create_plan(self, objective: str) -> Plan:
        cleaned = objective.strip()
        if not cleaned:
            raise ValueError("Objective must not be empty")

        steps = [
            f"Clarify objective: {cleaned}",
            "Select relevant tools",
            "Execute plan steps",
            "Summarize outcome",
        ]
        return Plan(objective=cleaned, steps=steps)
