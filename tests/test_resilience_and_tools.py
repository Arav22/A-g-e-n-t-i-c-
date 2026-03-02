import asyncio

from agentic_ai.resilience import CircuitBreaker, CircuitBreakerPolicy, RetryPolicy, TimeoutPolicy, call_with_resilience
from agentic_ai.tools.executor import ToolExecutor, execute_model_call
from agentic_ai.tools.policy import ToolPermissionPolicy


def test_tool_fallback_on_failure():
    async def broken_tool(payload):
        raise RuntimeError("boom")

    executor = ToolExecutor(
        tool_registry={"search": {"query": broken_tool}},
        permission_policy=ToolPermissionPolicy.from_mapping({"search": ["query"]}),
    )

    resp = asyncio.run(
        executor.execute(
            {"tool_name": "search", "action": "query", "payload": {"q": "x"}},
            fallback=lambda req, err: {"answer": "cached", "error_code": err.code},
        )
    )

    assert resp.ok is True
    assert resp.degraded is True
    assert resp.data["answer"] == "cached"


def test_policy_denied():
    async def tool(payload):
        return {"ok": True}

    executor = ToolExecutor(
        tool_registry={"search": {"query": tool}},
        permission_policy=ToolPermissionPolicy.from_mapping({"search": ["read"]}),
    )

    resp = asyncio.run(executor.execute({"tool_name": "search", "action": "query", "payload": {}}))
    assert resp.ok is False
    assert resp.error.code == "POLICY_DENIED"


def test_timeout_then_retry_exhausted():
    async def slow():
        await asyncio.sleep(0.05)
        return "x"

    try:
        asyncio.run(
            call_with_resilience(
                operation="model:test",
                call=slow,
                timeout_policy=TimeoutPolicy(timeout_seconds=0.001),
                retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=0.001),
            )
        )
        assert False, "Expected retry exhausted error"
    except Exception:
        pass


def test_model_fallback():
    async def broken_model(model_name, prompt, context):
        raise RuntimeError("down")

    resp = asyncio.run(
        execute_model_call(
            {"model_name": "gpt", "prompt": "hello"},
            model_call=broken_model,
            fallback=lambda req, err: "temporary response",
        )
    )

    assert resp.ok is True
    assert resp.degraded is True
    assert resp.output_text == "temporary response"


def test_circuit_opens_after_failures():
    async def bad_call():
        raise RuntimeError("fail")

    breaker = CircuitBreaker("tool:bad", CircuitBreakerPolicy(failure_threshold=1, recovery_timeout_seconds=60))

    try:
        asyncio.run(
            call_with_resilience(
                operation="tool:bad",
                call=bad_call,
                retry_policy=RetryPolicy(max_attempts=1),
                circuit_breaker=breaker,
            )
        )
    except Exception:
        pass

    try:
        asyncio.run(
            call_with_resilience(
                operation="tool:bad",
                call=bad_call,
                retry_policy=RetryPolicy(max_attempts=1),
                circuit_breaker=breaker,
            )
        )
        assert False, "Expected open circuit behavior"
    except Exception:
        pass
