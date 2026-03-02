"""Validated execution boundary for tool and model calls with graceful fallback."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from agentic_ai.errors import (
    AgenticError,
    ModelExecutionError,
    ToolExecutionError,
    ValidationError,
)
from agentic_ai.resilience import CircuitBreaker, RetryPolicy, TimeoutPolicy, call_with_resilience
from agentic_ai.tools.policy import ToolPermissionPolicy
from agentic_ai.tools.schemas import (
    ErrorPayload,
    ModelCallRequest,
    ModelCallResponse,
    ToolCallRequest,
    ToolCallResponse,
)


class ToolExecutor:
    def __init__(
        self,
        tool_registry: dict[str, dict[str, Callable[[dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]]],
        permission_policy: ToolPermissionPolicy,
    ) -> None:
        self.tool_registry = tool_registry
        self.permission_policy = permission_policy

    async def execute(
        self,
        request_payload: dict[str, Any],
        *,
        retry_policy: RetryPolicy | None = None,
        timeout_policy: TimeoutPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        fallback: Callable[[ToolCallRequest, AgenticError], dict[str, Any]] | None = None,
    ) -> ToolCallResponse:
        try:
            request = ToolCallRequest.model_validate(request_payload)
        except PydanticValidationError as exc:
            err = ValidationError("Invalid tool request payload.", details={"errors": exc.errors()})
            return ToolCallResponse(ok=False, error=ErrorPayload.model_validate(err.to_dict()))

        try:
            self.permission_policy.enforce(request.tool_name, request.action)
            tool = self.tool_registry[request.tool_name][request.action]

            result = await call_with_resilience(
                operation=f"tool:{request.tool_name}.{request.action}",
                call=lambda: tool(request.payload),
                retry_policy=retry_policy,
                timeout_policy=timeout_policy,
                circuit_breaker=circuit_breaker,
            )
            if not isinstance(result, dict):
                raise ValidationError(
                    "Tool returned non-dictionary output.", details={"output_type": type(result).__name__}
                )

            return ToolCallResponse(ok=True, data=result)
        except AgenticError as err:
            if fallback:
                fallback_data = fallback(request, err)
                return ToolCallResponse(
                    ok=True,
                    data=fallback_data,
                    degraded=True,
                    warnings=[f"Fallback used due to {err.code}."],
                )
            return ToolCallResponse(ok=False, error=ErrorPayload.model_validate(err.to_dict()))
        except KeyError as exc:
            err = ValidationError(
                "Requested tool/action is not registered.",
                details={"tool_name": request.tool_name, "action": request.action, "error": repr(exc)},
            )
            return ToolCallResponse(ok=False, error=ErrorPayload.model_validate(err.to_dict()))
        except Exception as exc:  # noqa: BLE001
            err = ToolExecutionError(request.tool_name, request.action, exc)
            if fallback:
                fallback_data = fallback(request, err)
                return ToolCallResponse(
                    ok=True,
                    data=fallback_data,
                    degraded=True,
                    warnings=["Tool failed; fallback response returned."],
                )
            return ToolCallResponse(ok=False, error=ErrorPayload.model_validate(err.to_dict()))


async def execute_model_call(
    request_payload: dict[str, Any],
    *,
    model_call: Callable[[str, str, dict[str, Any]], Awaitable[str] | str],
    retry_policy: RetryPolicy | None = None,
    timeout_policy: TimeoutPolicy | None = None,
    circuit_breaker: CircuitBreaker | None = None,
    fallback: Callable[[ModelCallRequest, AgenticError], str] | None = None,
) -> ModelCallResponse:
    try:
        request = ModelCallRequest.model_validate(request_payload)
    except PydanticValidationError as exc:
        err = ValidationError("Invalid model request payload.", details={"errors": exc.errors()})
        return ModelCallResponse(ok=False, error=ErrorPayload.model_validate(err.to_dict()))

    try:
        output_text = await call_with_resilience(
            operation=f"model:{request.model_name}",
            call=lambda: model_call(request.model_name, request.prompt, request.context),
            retry_policy=retry_policy,
            timeout_policy=timeout_policy,
            circuit_breaker=circuit_breaker,
        )
        return ModelCallResponse(ok=True, output_text=str(output_text))
    except AgenticError as err:
        if fallback:
            text = fallback(request, err)
            return ModelCallResponse(
                ok=True,
                output_text=text,
                degraded=True,
                warnings=[f"Fallback used due to {err.code}."],
            )
        return ModelCallResponse(ok=False, error=ErrorPayload.model_validate(err.to_dict()))
    except Exception as exc:  # noqa: BLE001
        err = ModelExecutionError(request.model_name, exc)
        if fallback:
            text = fallback(request, err)
            return ModelCallResponse(
                ok=True,
                output_text=text,
                degraded=True,
                warnings=["Model failed; fallback response returned."],
            )
        return ModelCallResponse(ok=False, error=ErrorPayload.model_validate(err.to_dict()))
