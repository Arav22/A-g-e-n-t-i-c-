from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Iterator

from .structured_logging import StructuredLogger


@dataclass(slots=True)
class TraceSpan:
    name: str
    started_at: float = field(default_factory=perf_counter)
    ended_at: float | None = None
    status: str = "ok"

    @property
    def duration_ms(self) -> float:
        end = self.ended_at if self.ended_at is not None else perf_counter()
        return (end - self.started_at) * 1000


class Tracer:
    """Minimal tracer producing span start/finish events."""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    @contextmanager
    def span(self, name: str, **fields: object) -> Iterator[TraceSpan]:
        span = TraceSpan(name=name)
        self.logger.info("span.start", event_type="span", span=name, phase=name, **fields)
        try:
            yield span
        except Exception:
            span.status = "error"
            span.ended_at = perf_counter()
            self.logger.error(
                "span.finish",
                event_type="span",
                span=name,
                phase=name,
                status=span.status,
                duration_ms=round(span.duration_ms, 2),
                **fields,
            )
            raise
        else:
            span.ended_at = perf_counter()
            self.logger.info(
                "span.finish",
                event_type="span",
                span=name,
                phase=name,
                status=span.status,
                duration_ms=round(span.duration_ms, 2),
                **fields,
            )
