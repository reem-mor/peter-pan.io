# Tools API demo data

Canonical structured data for the Tools API service. Six-service e-commerce/ops
universe: `shop-web`, `orders-api`, `payments-api` (App Platform), `postgres-primary`
(Database Reliability), `redis-cache`, `k8s-ingress` (Infra SRE). Two environments:
`production`, `staging`.

- `service_owners.csv`: owning team, on-call roles, Slack channel, PagerDuty id,
  runbook id, dashboard, dependencies, and compliance-framework exposure per service.
- `deploys.csv`: deployment history used for deploy correlation. Includes the
  coherent demo story: a bad `orders-api` deploy (`DEP-20260615-002`, rolled back)
  that triggers the P1 error-rate incident below.
- `alerts.csv`: summarized investigation-candidate alerts (one per notable event),
  including the P1 hero alert `ALERT-20260615-001` for the `orders-api` outage.
- `alert_stream.csv`: 400 deterministic alerts for the alert-storm demo; exactly
  one row (`ALT-20260615-0400`, `orders-api`) has `is_trigger=true` and matches the
  hero P1 alert above.
- `on_call_schedule.csv`: role-based on-call rotation (three 1-week rotations) with
  role titles only — no personal names or contact details.
- `past_incidents.csv`: sanitized historical incidents used for similar-incident
  matching, including the hero's own precedent (`INC-20251104-001`).
- `business_impact.json`: sanitized business-impact model (revenue/minute by
  priority, active users, compliance exposure) per service.
- `priority_matrix.json`: priority factors and P1-P4 thresholds.
- `escalation_policies.json`: escalation notify lists per priority plus
  compliance-framework overrides (`PCI-DSS`, `SOC2`) — generic frameworks, not
  jurisdiction-specific regulators.
- `runbooks_manifest.json`: existence-only list of runbook ids referenced by
  `service_owners.csv` / `past_incidents.csv`. Runbook *content* lives in the RAG
  service's corpus (`services/rag/corpus/`, a separate service reached over HTTP);
  this manifest only validates that a referenced id is known.

Safety: no credentials, personal names, phone numbers, raw emails, real customer
data, or internal secrets. Any live escalation recipients must be configured
outside git via environment variables (`PETER_ESCALATION_EMAIL` / `_SMS`); Tools
API itself never dispatches externally (`POST /escalations` is preview-only).
