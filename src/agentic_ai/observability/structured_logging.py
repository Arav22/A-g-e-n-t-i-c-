from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class JsonFormatter(logging.Formatter):
    """Formats log records as JSON payloads for easy machine parsing."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "run_id"):
            payload["run_id"] = record.run_id
        if hasattr(record, "correlation_id"):
            payload["correlation_id"] = record.correlation_id
        if hasattr(record, "step"):
            payload["step"] = record.step
        if hasattr(record, "event_type"):
            payload["event_type"] = record.event_type

        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


@dataclass(slots=True)
class RunContext:
    """Identifiers attached to all events emitted during one run."""

    run_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid4()))


class StructuredLogger:
    """Wrapper around stdlib logging with run/correlation IDs baked in."""

    def __init__(self, name: str, context: RunContext | None = None):
        self.context = context or RunContext()
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JsonFormatter())
            self._logger.addHandler(handler)
            self._logger.propagate = False
        self._logger.setLevel(logging.INFO)

    def emit(self, level: int, message: str, **fields: Any) -> None:
        self._logger.log(
            level,
            message,
            extra={
                "run_id": self.context.run_id,
                "correlation_id": self.context.correlation_id,
                "extra_fields": fields,
            },
        )

    def info(self, message: str, **fields: Any) -> None:
        self.emit(logging.INFO, message, **fields)

    def warning(self, message: str, **fields: Any) -> None:
        self.emit(logging.WARNING, message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self.emit(logging.ERROR, message, **fields)
