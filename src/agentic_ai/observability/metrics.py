from __future__ import annotations

import threading
from collections import Counter
from dataclasses import dataclass, field
from time import perf_counter, sleep
from typing import Callable


@dataclass(slots=True)
class StepCounters:
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0


@dataclass
class MetricsStore:
    runs_total: int = 0
    success_total: int = 0
    retries_total: int = 0
    failures_by_class: Counter[str] = field(default_factory=Counter)
    latency_ms: list[float] = field(default_factory=list)

    def observe_run(self, *, success: bool, latency_ms: float, failure_class: str | None = None) -> None:
        self.runs_total += 1
        self.latency_ms.append(latency_ms)
        if success:
            self.success_total += 1
        elif failure_class:
            self.failures_by_class[failure_class] += 1

    def observe_retry(self) -> None:
        self.retries_total += 1

    def snapshot(self) -> dict[str, object]:
        avg_latency = sum(self.latency_ms) / len(self.latency_ms) if self.latency_ms else 0.0
        success_rate = (self.success_total / self.runs_total) if self.runs_total else 0.0
        return {
            "runs_total": self.runs_total,
            "success_total": self.success_total,
            "success_rate": round(success_rate, 4),
            "retries_total": self.retries_total,
            "avg_latency_ms": round(avg_latency, 2),
            "failures_by_class": dict(self.failures_by_class),
        }


class PeriodicMetricReporter:
    """Emits metrics at a fixed cadence when endpoint export is unavailable."""

    def __init__(self, emit: Callable[[dict[str, object]], None], store: MetricsStore, interval_s: int = 30):
        self.emit = emit
        self.store = store
        self.interval_s = interval_s
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            sleep(self.interval_s)
            self.emit(self.store.snapshot())


class StepTimer:
    def __init__(self) -> None:
        self._start = perf_counter()

    def elapsed_ms(self) -> float:
        return (perf_counter() - self._start) * 1000
