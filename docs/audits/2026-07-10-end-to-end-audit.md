# PETER PAN — End-to-End Audit (2026-07-10)

## Baseline QA (pre-hardening)

Re-verified on 2026-07-11 from the repository virtual environment:

| Check | Result |
|---|---|
| `python -m ruff check .` | PASS |
| `python scripts/run_all_tests.py` | PASS — 8 service suites; dependency deprecation warnings remain |
| `python docs/contracts/export_json_schema.py` + schema diff | PASS — no schema drift |
| `docker compose config` | PASS syntax; FAIL security review — usable secret defaults are rendered |
| `python evaluation/run_e2e.py --dry-run` | PASS — 3 fixtures loaded; no HTTP or n8n execution |
| `cfn-lint infra/aws/template.yaml` | FAIL — invalid Unicode in `GroupDescription` and two unnecessary `Fn::Sub` warnings |

The full compose-backed n8n path was not exercised at this baseline. No full-E2E
or coverage claim is valid until the Stage A integration gate is implemented and run.

## Post-hardening verification (2026-07-11)

| Check | Result |
|---|---|
| `python scripts/run_all_tests.py` | PASS — 553 tests across 8 services, observability, UI, n8n, and evaluation |
| Coverage gates | PASS — every Python deployment unit/UI/evaluation suite enforces ≥80%; measured range 82–99% |
| `ruff check .` | PASS |
| Contract schema export + diff | PASS — no drift |
| Local + CI `docker compose config --quiet` | PASS with required/generated environment values |
| `cfn-lint infra/aws/template.yaml` | PASS |
| `evaluation/run_e2e.py --dry-run` | PASS — 7 frozen scenarios |
| Compose-backed n8n E2E | PASS — 7/7 scenarios: app, DB, infra/LangGraph, reject, suppress, review, P1 preview |
| Streamlit Playwright smoke | PASS — UI loaded; five service health checks and webhook configuration were green |

The local virtual environment is Python 3.14.5 while CI remains pinned to the project
target, Python 3.12. The suites pass locally, but Starlette TestClient and LangGraph emit
upstream deprecation warnings on Python 3.14.

AWS cfn-guard reduced from nine to three findings. The remaining findings are declared
single-instance demo trade-offs: public-subnet IP assignment, the internet-gateway default
route, and HTTPS egress. Ingress requires one explicit public IPv4 `/32`;
Bedrock IAM access is scoped to Anthropic foundation-model ARNs and disabled by default.

Read-only AWS account audit: the credential chain authenticated, account-side
CloudFormation validation passed, Claude Sonnet is authorized in `us-east-1`, and no
PETER PAN stack, EC2 instance, IAM role, or Bedrock Guardrail is currently deployed.
No model invocation or resource mutation was performed.

Update (2026-07-11, post-audit): the demo instance was provisioned after the read-only
audit above. The Stage A demo EC2 instance is currently running, and the full n8n-path
E2E passed 7/7 on EC2 on 2026-07-11.

## Understanding lock (confirmed)

- Complete all four layers with fixture-first validation; no live AWS provisioning.
- Portfolio VPC demo: ≤5 users, ≤1 signal/sec, synthetic data only.
- Zero predecessor-project references in active code/config/docs.
- Six services with four graded primary capabilities (fourth declared deviation).

## File disposition manifest

| Path | Action | Rationale |
|---|---|---|
| `services/{ingestion,predictor,rag,guardrails,tools-api,langgraph-agent}/` | **Keep + harden** | Layer 3 foundation; suites green |
| `docs/contracts/` | **Keep** | Frozen contracts |
| `n8n/peter-flow.json` | **Keep + update** | Layer 2 source of record |
| `.env.example` | **Rewrite** | Legacy template |
| Retired carryover ADR | **Removed** | Superseded by ADR 0002/0003 and this audit |
| `evaluation/*.json` | **Rewrite + extend** | Stale tool names |
| `evaluation/run_e2e.py` | **Generate** | Stage A exit gate |
| `services/fixture-llm/` | **Generate** | n8n mock seam |
| `ui/` | **Generate** | Layer 1 Streamlit |
| `infra/aws/` | **Generate** | CloudFormation demo stack |
| Retired course/archive skills | **Removed** | Outside this repository's scope |
| `.cursor/mcp.json` | **Untrack** | Local secrets risk |

## Decision log

| Decision | Alternatives | Why |
|---|---|---|
| Controlled hardening | Clean-room rebuild | Preserves green suites |
| n8n sole orchestrator | Predictor→n8n direct | Matches BUILD_PLAN resolution |
| FixtureLLM OpenAI-compatible | Inline n8n Code nodes | Reusable across services |
| CloudFormation YAML | CDK/Terraform | Minimal deps per plan |
| Circuit breakers on egress only | Every boundary | Proportional ops |

## Open risks

- Single-node AWS cannot provide HA.
- Full llama.cpp 7B exceeds `t3.large` fixture-mode sizing.
- The Stage A writer uses a tested tool-grounded fallback when the local structured
  parser rejects the fixture response.

## Remaining rubric gaps

- Screenshot and fallback-video artifacts were not produced; browser smoke validation is recorded instead.
- Bedrock Sonnet was not invoked because it is optional Stage C scope, not a Layers 2–3 dependency.
- PyTorch training/accuracy evidence, the 55+ document corpus, and the complete prompt-engineering log remain planned.

These gaps do not invalidate the verified fixture-backed Stage A gate and must not be
described as completed in a merge request or presentation.
