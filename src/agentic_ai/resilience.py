"""Timeout, retry, and circuit-breaker utilities for model and tool calls."""

from __future__ import annotations

import asyncio
import inspect
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, TypeVar

from .errors import CircuitOpenError, RetryExhaustedError, TimeoutError

T = TypeVar("T")


@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 0.5
    backoff_multiplier: float = 2.0
    max_backoff_seconds: float = 5.0

    def sleep_for_attempt(self, attempt: int) -> float:
        raw = self.backoff_seconds * (self.backoff_multiplier ** max(attempt - 1, 0))
        return min(raw, self.max_backoff_seconds)


@dataclass(slots=True)
class TimeoutPolicy:
    timeout_seconds: float = 20.0


@dataclass(slots=True)
class CircuitBreakerPolicy:
    failure_threshold: int = 3
    recovery_timeout_seconds: float = 30.0


class CircuitBreaker:
    def __init__(self, operation: str, policy: CircuitBreakerPolicy | None = None) -> None:
        self.operation = operation
        self.policy = policy or CircuitBreakerPolicy()
        self._failure_count = 0
        self._opened_at: float | None = None

    def can_execute(self) -> bool:
        if self._opened_at is None:
            return True
        elapsed = time.monotonic() - self._opened_at
        if elapsed >= self.policy.recovery_timeout_seconds:
            self._opened_at = None
            self._failure_count = 0
            return True
        return False

    def check(self) -> None:
        if not self.can_execute():
            remaining = self.policy.recovery_timeout_seconds - (time.monotonic() - (self._opened_at or 0))
            raise CircuitOpenError(self.operation, max(remaining, 0.0))

    def record_success(self) -> None:
        self._failure_count = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self.policy.failure_threshold:
            self._opened_at = time.monotonic()


async def _execute(call: Callable[[], T] | Callable[[], Awaitable[T]]) -> T:
    result = call()
    if inspect.isawaitable(result):
        return await result
    return result


async def call_with_resilience(
    operation: str,
    call: Callable[[], T] | Callable[[], Awaitable[T]],
    *,
    retry_policy: RetryPolicy | None = None,
    timeout_policy: TimeoutPolicy | None = None,
    circuit_breaker: CircuitBreaker | None = None,
) -> T:
    retry_policy = retry_policy or RetryPolicy()
    timeout_policy = timeout_policy or TimeoutPolicy()

    last_error: Exception | None = None
    for attempt in range(1, retry_policy.max_attempts + 1):
        if circuit_breaker:
            circuit_breaker.check()

        try:
            result = await asyncio.wait_for(_execute(call), timeout=timeout_policy.timeout_seconds)
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
        except asyncio.TimeoutError as exc:
            error = TimeoutError(operation, timeout_policy.timeout_seconds)
            last_error = error
            if circuit_breaker:
                circuit_breaker.record_failure()
            if attempt == retry_policy.max_attempts:
                break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if circuit_breaker:
                circuit_breaker.record_failure()
            if attempt == retry_policy.max_attempts:
                break

        await asyncio.sleep(retry_policy.sleep_for_attempt(attempt))

    raise RetryExhaustedError(operation, retry_policy.max_attempts, last_error)
