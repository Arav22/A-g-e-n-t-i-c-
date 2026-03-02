"""Error hierarchy with user-facing messages and machine-readable codes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgenticError(Exception):
    """Base error for all agentic runtime failures."""

    code: str
    message: str
    user_message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "user_message": self.user_message or self.message,
            "retryable": self.retryable,
        }
        if self.details:
            payload["details"] = self.details
        return payload


class ValidationError(AgenticError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            user_message="The request format is invalid. Please check input fields and try again.",
            details=details or {},
            retryable=False,
        )


class PolicyDeniedError(AgenticError):
    def __init__(self, tool_name: str, action: str) -> None:
        super().__init__(
            code="POLICY_DENIED",
            message=f"Action '{action}' is not allowed for tool '{tool_name}'.",
            user_message="That action is not allowed by the current tool permission policy.",
            details={"tool_name": tool_name, "action": action},
            retryable=False,
        )


class TimeoutError(AgenticError):
    def __init__(self, operation: str, timeout_seconds: float) -> None:
        super().__init__(
            code="TIMEOUT",
            message=f"{operation} timed out after {timeout_seconds:.2f}s.",
            user_message="The operation took too long and timed out. Please try again.",
            details={"operation": operation, "timeout_seconds": timeout_seconds},
            retryable=True,
        )


class RetryExhaustedError(AgenticError):
    def __init__(self, operation: str, attempts: int, last_error: Exception | None = None) -> None:
        super().__init__(
            code="RETRY_EXHAUSTED",
            message=f"{operation} failed after {attempts} attempts.",
            user_message="We couldn't complete your request after several retries.",
            details={
                "operation": operation,
                "attempts": attempts,
                "last_error": repr(last_error) if last_error else None,
            },
            retryable=True,
        )


class CircuitOpenError(AgenticError):
    def __init__(self, operation: str, reopen_after_seconds: float) -> None:
        super().__init__(
            code="CIRCUIT_OPEN",
            message=(
                f"Circuit is open for '{operation}'. "
                f"Retry after {reopen_after_seconds:.2f}s."
            ),
            user_message="This service is temporarily unavailable. Please try again shortly.",
            details={"operation": operation, "reopen_after_seconds": reopen_after_seconds},
            retryable=True,
        )


class ToolExecutionError(AgenticError):
    def __init__(self, tool_name: str, action: str, error: Exception) -> None:
        super().__init__(
            code="TOOL_EXECUTION_FAILED",
            message=f"Tool '{tool_name}' action '{action}' failed: {error}",
            user_message="A tool failed while processing your request.",
            details={"tool_name": tool_name, "action": action, "error": repr(error)},
            retryable=True,
        )


class ModelExecutionError(AgenticError):
    def __init__(self, model_name: str, error: Exception) -> None:
        super().__init__(
            code="MODEL_EXECUTION_FAILED",
            message=f"Model '{model_name}' failed: {error}",
            user_message="The AI model is currently unavailable.",
            details={"model_name": model_name, "error": repr(error)},
            retryable=True,
        )
