from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class StepAttempt:
    strategy: str
    output: str | None = None
    success: bool = False
    error: str | None = None
    timestamp: str = field(default_factory=_utc_now)


@dataclass(slots=True)
class StepState:
    id: str
    description: str
    tool: str
    status: str = "pending"
    strategy: str = "default"
    attempts: list[StepAttempt] = field(default_factory=list)


@dataclass(slots=True)
class RunState:
    objective: str
    run_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    status: str = "created"
    current_step: int = 0
    steps: list[StepState] = field(default_factory=list)
    logs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def record_phase(self, phase: str, message: str, **details: Any) -> None:
        self.logs.append(
            {
                "timestamp": _utc_now(),
                "phase": phase,
                "message": message,
                "details": details,
            }
        )
        self.updated_at = _utc_now()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RunStateStore:
    """JSON persistence utility for resumable run state."""

    def __init__(self, storage_dir: str | Path) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, run_id: str) -> Path:
        return self.storage_dir / f"{run_id}.json"

    def save(self, state: RunState) -> Path:
        state.updated_at = _utc_now()
        target = self.path_for(state.run_id)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(state.to_dict(), handle, indent=2)
        return target

    def load(self, run_id: str) -> RunState:
        target = self.path_for(run_id)
        with target.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return self._hydrate(payload)

    def _hydrate(self, payload: dict[str, Any]) -> RunState:
        steps = []
        for step in payload.get("steps", []):
            attempts = [StepAttempt(**attempt) for attempt in step.get("attempts", [])]
            steps.append(StepState(attempts=attempts, **{k: v for k, v in step.items() if k != "attempts"}))

        return RunState(
            objective=payload["objective"],
            run_id=payload["run_id"],
            created_at=payload.get("created_at", _utc_now()),
            updated_at=payload.get("updated_at", _utc_now()),
            status=payload.get("status", "created"),
            current_step=payload.get("current_step", 0),
            steps=steps,
            logs=payload.get("logs", []),
            metadata=payload.get("metadata", {}),
        )
