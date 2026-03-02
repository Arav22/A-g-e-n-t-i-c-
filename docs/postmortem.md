# Postmortem: Misrouted Escalation in Workflow Automation

## Incident Summary
- **Date:** 2026-02-18
- **Use case:** Workflow automation (customer escalation)
- **Impact:** A billing data-integrity ticket was incorrectly routed only to Support Engineering, delaying Data Platform involvement by 42 minutes.

## What Happened
The agent received a ticket indicating duplicated invoices with financial impact. The routing rules required Data Platform involvement when data integrity is uncertain. The generated answer assigned `SEV-2` correctly but omitted the Data Platform team from routed ownership.

## Root Cause
- The prompt template contained the routing rule, but evaluator checks only validated severity and SLA fields.
- No explicit assertion existed for mandatory co-routing in data-integrity scenarios.

## Detection
- Detected by benchmark regression run where policy adherence score dropped from 0.93 to 0.76.
- Trace logs showed `rule_match:data_integrity=true` but `routed_teams=[billing]`.

## Self-Correction Mechanism
The agent self-corrected in a second attempt via rule-aware retry logic:

1. Evaluator flagged violation: `missing_required_team:data-platform`.
2. Retry planner injected corrective hint: "Include Data Platform for uncertain integrity incidents."
3. Regenerated output routed to `Billing + Data Platform` and passed policy checks.

## Preventive Actions
1. Add strict evaluator assertion for required co-routing.
2. Promote routing-policy checks to blocking gates before final response.
3. Add regression fixture for duplicated-invoice scenarios.
4. Surface policy violations in operator dashboard with alerting.
