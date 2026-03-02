from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Iterator

from .metrics import MetricsStore, StepCounters, StepTimer
from .structured_logging import RunContext, StructuredLogger
from .tracing import Tracer


TRACE_PLAN = "plan_generation"
TRACE_TOOL = "tool_invocation"
TRACE_CRITIQUE = "critique"


@dataclass
class ObservabilityRuntime:
    logger_name: str = "agentic_ai"
    context: RunContext = field(default_factory=RunContext)
    metrics: MetricsStore = field(default_factory=MetricsStore)

    def __post_init__(self) -> None:
        self.logger = StructuredLogger(self.logger_name, context=self.context)
        self.tracer = Tracer(self.logger)

    def start_run(self, prompt: str) -> float:
        started_at = perf_counter()
        self.logger.info("run.start", event_type="run", prompt=prompt)
        return started_at

    def finish_run(self, started_at: float, *, success: bool, failure_class: str | None = None) -> None:
        latency_ms = (perf_counter() - started_at) * 1000
        self.metrics.observe_run(success=success, latency_ms=latency_ms, failure_class=failure_class)
        self.logger.info(
            "run.finish",
            event_type="run",
            success=success,
            latency_ms=round(latency_ms, 2),
            failure_class=failure_class,
        )

    def record_retry(self, reason: str) -> None:
        self.metrics.observe_retry()
        self.logger.warning("run.retry", event_type="run", reason=reason)

    @contextmanager
    def step(self, step: str, **fields: Any) -> Iterator[StepCounters]:
        timer = StepTimer()
        counters = StepCounters()
        yield counters
        counters.latency_ms = timer.elapsed_ms()
        self.logger.info(
            "step.finish",
            event_type="step",
            step=step,
            tokens_in=counters.tokens_in,
            tokens_out=counters.tokens_out,
            cost_usd=round(counters.cost_usd, 6),
            latency_ms=round(counters.latency_ms, 2),
            **fields,
        )
