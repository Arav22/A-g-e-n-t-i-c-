"""API-level request and response models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TaskRequest:
    prompt: str


@dataclass
class TaskResponse:
    output: str
