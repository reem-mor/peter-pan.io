# ADR 0004 — Guardrail result and predictor taxonomy contracts

- **Status:** accepted (2026-07-11)
- **Context:** The canonical contracts omitted the Guardrails response, while Predictor
  `category` was overloaded between six incident classes and three routing buckets. This allowed
  wire-shape and routing-policy drift across services, n8n, tests, and agent instructions.

## Decision

1. Add this frozen response to `docs/contracts/contracts.py` and every vendored contract copy:
   - `passed: bool`
   - `flags: list[str]`
   - `reason: str` with a 500-character maximum
2. Both Guardrails endpoints return the canonical field name `passed`. The previous `pass` alias is
   removed. Every violation flag remains present; human-readable reasons are bounded before model
   validation.
3. Predictor `/analyse` returns `incident_class`, not `category`, using the fixed six-class enum:
   `cpu_saturation`, `memory_leak`, `db_lock_contention`, `replication_lag`,
   `error_rate_spike`, and `normal`.
4. n8n owns the deterministic class-to-route policy:
   - CPU saturation and memory leak → `infra`
   - DB lock contention and replication lag → `database`
   - Error-rate spike → `application`
   - Normal → suppress without team, Slack, or escalation dispatch
5. Unknown model classes are normalized to `normal` with low confidence and an
   `unknown_class` fallback marker. A `normal` class that conflicts with EWMA severity carries a
   `severity_conflict` marker. n8n treats any fallback marker, missing observation, inconsistent
   severity, and malformed response as invalid and fails closed before report generation. The frozen
   `TriageReport.category` contract remains unchanged.

## Consequences

- Guardrails clients must consume `passed`; this is an intentional breaking correction of a
  previously unfrozen response.
- Predictor clients cannot treat model output as a routing category.
- Routing is deterministic and unit/static-tested; the report writer cannot choose a category.
- The Stage-A fixed classifier may use explicit metric/symptom context until the trained T1 model
  replaces that seam. It must still emit only the six allowed values.
- Contract JSON Schemas are regenerated and every service vendor remains byte-identical.

## Related decisions

- [ADR 0003 — System boundaries and service inventory](0003-system-boundaries.md)
- [Documentation reconciliation F2–F3](../archive/DOCS-RECONCILIATION.md)
