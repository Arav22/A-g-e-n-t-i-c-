from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any

from agentic_ai.orchestrator.critic import StepCritic
from agentic_ai.orchestrator.state import RunState, RunStateStore, StepAttempt, StepState
from agentic_ai.tools.registry import ToolRegistry, default_registry


@dataclass(slots=True)
class EngineConfig:
    max_retries: int = 3
    backoff_seconds: float = 0.2


class OrchestrationEngine:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
        critic: StepCritic | None = None,
        store: RunStateStore | None = None,
        config: EngineConfig | None = None,
    ) -> None:
        self.registry = registry or default_registry()
        self.critic = critic or StepCritic()
        self.store = store or RunStateStore(".runs")
        self.config = config or EngineConfig()

    def start(self, objective: str) -> RunState:
        state = RunState(objective=objective)
        state.steps = self.build_plan(objective)
        state.status = "planned"
        state.record_phase("plan", "Plan generated", steps=len(state.steps))
        self.store.save(state)
        return self.run(state)

    def resume(self, run_id: str) -> RunState:
        state = self.store.load(run_id)
        return self.run(state)

    def build_plan(self, objective: str) -> list[StepState]:
        fragments = [f.strip() for f in objective.split(" then ") if f.strip()]
        if not fragments:
            fragments = [objective.strip()]
        if not fragments[0]:
            fragments = ["Clarify the objective"]

        steps = []
        for idx, fragment in enumerate(fragments, start=1):
            tool = "search" if any(word in fragment.lower() for word in ("find", "research", "lookup")) else "reason"
            steps.append(StepState(id=f"step-{idx}", description=fragment, tool=tool))
        return steps

    def run(self, state: RunState) -> RunState:
        state.status = "running"
        for idx in range(state.current_step, len(state.steps)):
            step = state.steps[idx]
            state.current_step = idx
            if step.status == "completed":
                continue
            success = self._execute_step(state, step)
            self.store.save(state)
            if not success:
                state.status = "blocked"
                state.record_phase("revise", "Execution halted due to failed step", step=step.id)
                self.store.save(state)
                return state

        state.status = "completed"
        state.record_phase("revise", "All steps completed")
        self.store.save(state)
        return state

    def _execute_step(self, state: RunState, step: StepState) -> bool:
        for attempt_num in range(self.config.max_retries):
            state.record_phase(
                "act",
                "Executing step",
                step=step.id,
                attempt=attempt_num + 1,
                tool=step.tool,
                strategy=step.strategy,
            )

            prompt = self._render_prompt(step.description, step.strategy)
            try:
                output = self.registry.run(step.tool, prompt, {"objective": state.objective, "run_id": state.run_id})
                critic_result = self.critic.evaluate(output, state.objective, step.description, attempt_num)
                attempt = StepAttempt(strategy=step.strategy, output=output, success=critic_result.passed)
                step.attempts.append(attempt)
                state.record_phase(
                    "observe",
                    "Critic evaluated step output",
                    step=step.id,
                    passed=critic_result.passed,
                    feedback=critic_result.feedback,
                )
                if critic_result.passed:
                    step.status = "completed"
                    return True
                step.strategy = critic_result.next_strategy
            except Exception as exc:  # noqa: BLE001
                step.attempts.append(StepAttempt(strategy=step.strategy, success=False, error=str(exc)))
                state.record_phase("observe", "Tool execution error", step=step.id, error=str(exc))

            step.status = "retrying"
            if attempt_num < self.config.max_retries - 1:
                delay = min(self.config.backoff_seconds * (2**attempt_num), 2.0)
                state.record_phase("revise", "Retrying step with backoff", step=step.id, delay=delay)
                time.sleep(delay)

        step.status = "failed"
        return False

    @staticmethod
    def _render_prompt(step_description: str, strategy: str) -> str:
        if strategy == "exploratory":
            return f"Explore multiple approaches for: {step_description}"
        if strategy == "concise":
            return f"Produce a concise result for: {step_description}"
        return step_description


def run_objective(objective: str, run_dir: str = ".runs") -> RunState:
    engine = OrchestrationEngine(store=RunStateStore(run_dir))
    return engine.start(objective)
