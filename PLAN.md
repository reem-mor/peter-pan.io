# Reconciliation Steps 4–5

## Scope

1. Add the frozen `GuardrailResult` model to the canonical contracts, export its JSON Schema,
   synchronize every byte-identical service vendor, and use it as the Guardrails response model.
2. Change Predictor `/analyse` to a typed response whose fine-grained field is
   `incident_class` with the fixed six-class enum.
3. Derive `TriageReport.category` only through deterministic policy:
   `cpu_saturation|memory_leak -> infra`,
   `db_lock_contention|replication_lag -> database`,
   `error_rate_spike -> application`, and `normal -> suppressed`.
4. Update local n8n/fixture consumers and tests for the renamed response field without changing
   the frozen `TriageReport` shape or weakening deterministic safety floors.

## Execution

1. Add or update focused tests and confirm they fail for the missing contract/behavior.
2. Make the smallest implementation changes needed for those tests.
3. Regenerate the new contract schema and keep vendored contract files byte-identical.
4. Run Guardrails contract identity, Predictor, FixtureLLM, n8n static, evaluation, and lint checks
   affected by the contract/field migration.

## Success criteria

- `GuardrailResult` is canonical, exported, and byte-identical in every service contract vendor.
- Guardrails returns `passed`, `flags`, and `reason` through the canonical response model.
- Predictor OpenAPI exposes `incident_class` and never exposes the old routing `category`.
- All six incident classes have an explicit deterministic routing outcome; `normal` is not sent to
  an infra/database/application route.
- Focused tests and lint checks pass with no secrets or unrelated changes introduced.
