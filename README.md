# Agentic AI

## Observability

The `src/agentic_ai/observability/` package adds production-oriented telemetry primitives:

- Structured JSON logs with `run_id` and `correlation_id` fields on every event.
- Step-level token/cost counters (`tokens_in`, `tokens_out`, `cost_usd`) with latency timing.
- Trace spans for the key phases: `plan_generation`, `tool_invocation`, and `critique`.
- Metrics aggregation for success-rate, retries, latency, and failure classes via snapshots or periodic metric logs.

### How to inspect a run

1. Create a runtime and start a run:

```python
from agentic_ai.observability import ObservabilityRuntime, TRACE_PLAN, TRACE_TOOL, TRACE_CRITIQUE

runtime = ObservabilityRuntime()
run_started = runtime.start_run("Summarize incidents from yesterday")
```

2. Wrap each phase in spans and track counters per step:

```python
with runtime.tracer.span(TRACE_PLAN):
    with runtime.step("plan") as step:
        step.tokens_in += 820
        step.tokens_out += 140
        step.cost_usd += 0.0014

with runtime.tracer.span(TRACE_TOOL, tool="search_api"):
    with runtime.step("invoke_search_api") as step:
        step.tokens_in += 90
        step.tokens_out += 20
        step.cost_usd += 0.0002

with runtime.tracer.span(TRACE_CRITIQUE):
    with runtime.step("critique") as step:
        step.tokens_in += 220
        step.tokens_out += 80
        step.cost_usd += 0.0007
```

3. Finish the run and inspect snapshots:

```python
runtime.finish_run(run_started, success=True)
print(runtime.metrics.snapshot())
```

4. Optional periodic metric logs:

```python
from agentic_ai.observability import PeriodicMetricReporter

reporter = PeriodicMetricReporter(lambda snapshot: runtime.logger.info("metrics.snapshot", event_type="metrics", **snapshot), runtime.metrics, interval_s=15)
reporter.start()
```

### Sample trace output

```json
{"timestamp":"2026-01-15T19:04:10.101Z","level":"INFO","logger":"agentic_ai","message":"run.start","run_id":"7f2c...","correlation_id":"33ab...","event_type":"run","prompt":"Summarize incidents from yesterday"}
{"timestamp":"2026-01-15T19:04:10.123Z","level":"INFO","logger":"agentic_ai","message":"span.start","run_id":"7f2c...","correlation_id":"33ab...","event_type":"span","span":"plan_generation","phase":"plan_generation"}
{"timestamp":"2026-01-15T19:04:10.341Z","level":"INFO","logger":"agentic_ai","message":"step.finish","run_id":"7f2c...","correlation_id":"33ab...","event_type":"step","step":"plan","tokens_in":820,"tokens_out":140,"cost_usd":0.0014,"latency_ms":218.04}
{"timestamp":"2026-01-15T19:04:10.347Z","level":"INFO","logger":"agentic_ai","message":"span.finish","run_id":"7f2c...","correlation_id":"33ab...","event_type":"span","span":"plan_generation","phase":"plan_generation","status":"ok","duration_ms":224.00}
{"timestamp":"2026-01-15T19:04:10.912Z","level":"INFO","logger":"agentic_ai","message":"run.finish","run_id":"7f2c...","correlation_id":"33ab...","event_type":"run","success":true,"latency_ms":811.40,"failure_class":null}
{"timestamp":"2026-01-15T19:04:15.000Z","level":"INFO","logger":"agentic_ai","message":"metrics.snapshot","run_id":"7f2c...","correlation_id":"33ab...","event_type":"metrics","runs_total":1,"success_total":1,"success_rate":1.0,"retries_total":0,"avg_latency_ms":811.4,"failures_by_class":{}}
```
