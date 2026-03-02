# Use Case: Incident Triage Assistant

## Scenario
A Site Reliability Engineer asks the agent to triage a spike in 500 errors in the payments API.

## Reproducible Input Prompt
```text
You are an on-call incident assistant.
Given these metrics and logs, produce:
1) likely root cause,
2) immediate mitigation,
3) rollback decision,
4) follow-up tasks with owners.

Metrics:
- error_rate(payments-api): 0.4% -> 8.7% in 12 minutes
- p95 latency: 220ms -> 1450ms
- deploy event: payments-api v1.42.0 at 14:02 UTC
- db cpu: 68% -> 93%

Logs:
- Timeout acquiring DB connection from pool (pool exhausted)
- New query path: SELECT * FROM invoices WHERE customer_id=$1 ORDER BY created_at DESC

Constraints:
- Keep customer-facing impact below 15 minutes.
- Do not perform schema migrations during incident response.
```

## Expected Output (Golden)
- Flags likely root cause as inefficient query path introduced in `v1.42.0` causing connection pool exhaustion.
- Recommends immediate mitigation: rollback to `v1.41.x`, lower traffic via rate limiting, and temporary pool cap increase if safe.
- Decides **rollback now** due to elevated error rate and latency.
- Provides follow-up tasks: query optimization, index review, load test gate in CI, and postmortem owner assignment.

## Evaluation Criteria
- **Correctness (40%)**: Root cause maps to deploy + query evidence.
- **Actionability (30%)**: Mitigation is concrete and prioritized.
- **Safety (20%)**: Avoids risky actions during incident (e.g., no schema migration).
- **Clarity (10%)**: Response is concise, ordered, and owner-tagged.
