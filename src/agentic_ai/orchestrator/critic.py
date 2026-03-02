from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CriticResult:
    passed: bool
    feedback: str
    next_strategy: str = "default"


class StepCritic:
    """Simple output evaluator used by the orchestration engine."""

    def evaluate(self, output: str, objective: str, step_description: str, attempts: int) -> CriticResult:
        if output and objective.lower().split()[0] in output.lower():
            return CriticResult(True, "Output aligned with objective signal")

        if attempts == 0:
            return CriticResult(
                False,
                "Weak objective alignment; retry with exploratory strategy",
                next_strategy="exploratory",
            )

        if attempts == 1:
            return CriticResult(
                False,
                "Need a concise revision emphasizing objective keywords",
                next_strategy="concise",
            )

        return CriticResult(False, "Exceeded useful retries for this step", next_strategy="default")
