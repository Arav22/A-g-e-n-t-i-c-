# Use Case: Workflow Automation for Customer Escalations

## Scenario
Support operations wants the agent to automate escalation routing for high-priority customer tickets.

## Reproducible Input Prompt
```text
Given the ticket payload below, decide escalation path and produce:
- severity (SEV-1..SEV-4),
- routed team,
- SLA target,
- customer-facing response draft,
- internal action checklist.

Ticket payload:
- customer_tier: enterprise
- region: eu-west
- product: billing
- issue: invoices duplicated after API sync
- impact: finance team blocked; 37 invoices affected
- related incidents: none in last 30 days

Rules:
- Enterprise billing data issues with financial impact >= 20 records should be SEV-1 or SEV-2.
- If data integrity is uncertain, involve data platform team.
- Customer update must be sent within 30 minutes.
```

## Expected Output (Golden)
- Assigns severity **SEV-2** (or justified SEV-1).
- Routes to Billing + Data Platform with explicit SLA.
- Produces empathetic customer response with timeframe and next update commitment.
- Provides checklist including audit, containment, and reconciliation steps.

## Evaluation Criteria
- **Policy adherence (45%)**: Follows severity/routing rules.
- **Operational readiness (30%)**: Checklist is executable.
- **Customer communication (15%)**: Message tone and clarity.
- **Timeliness awareness (10%)**: Includes 30-minute response requirement.
