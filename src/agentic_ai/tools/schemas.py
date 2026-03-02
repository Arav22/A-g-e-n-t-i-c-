"""Pydantic schemas for tool boundaries (input and output)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(description="Machine-readable error code.")
    message: str = Field(description="Internal error message.")
    user_message: str = Field(description="User-facing safe message.")
    retryable: bool = Field(default=False)
    details: dict[str, Any] | None = Field(default=None)


class ToolCallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(min_length=1)
    action: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    data: dict[str, Any] | None = None
    error: ErrorPayload | None = None
    degraded: bool = False
    warnings: list[str] = Field(default_factory=list)


class ModelCallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)


class ModelCallResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    output_text: str | None = None
    error: ErrorPayload | None = None
    degraded: bool = False
    warnings: list[str] = Field(default_factory=list)
