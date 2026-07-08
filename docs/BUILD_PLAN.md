# PETER PAN — Build Plan

- **Status:** proposed (2026-07-09) — awaiting approval before any Stage A implementation.
- **Source of truth:** [peter-pan-system.mmd](peter-pan-system.mmd) · [peter-pan-n8n-flow.mmd](peter-pan-n8n-flow.mmd).
  Anything not in the diagrams is out of scope. Carryover decisions: [ADR 0001](adr/0001-piter-carryover.md).
- **Build order (fixed, do not reorder):** Stage A (Layers 2+3, mock-first) → Stage B (Layer 1 UI) → Stage C (Layer 4 real LLM providers).

---

## 1 · Contracts first

Every layer speaks only these three models. They are **frozen at the start of Stage A**; changing
one afterwards requires an ADR. They live in a single shared file vendored into each service
(`<service>/<pkg>/contracts.py` — copied, not imported across services; a contract test asserts
the copies are identical) plus one canonical copy in `docs/contracts/contracts.py` exported to
JSON Schema for n8n's Structured Output Parser node.

```python
"""PETER PAN shared contracts — pydantic v2. Frozen at Stage A start."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Signal(BaseModel):
    """Anything that enters the system: Grafana alert, WebUI form, deploy event, complaint."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^sig-[a-z0-9-]{8,}$")
    source: Literal["grafana", "webui", "github", "slack"]
    kind: Literal["alert", "manual", "deploy_event", "complaint"]
    received_at: datetime
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(default="", max_length=8000)
    service: str | None = None          # normalized service slug when known
    environment: str | None = None      # e.g. "production" | "staging"
    severity_hint: Literal["critical", "warning", "info"] | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)  # original payload, never interpreted downstream


class DeployRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repo: str
    sha: str
    deployed_at: datetime
    service: str


class IncidentContext(BaseModel):
    """Output of the n8n context-enrichment branches (nodes MW/DEP/CMP → merge)."""
    model_config = ConfigDict(extra="forbid")
    maintenance_window: bool = False
    recent_deploys: list[DeployRef] = Field(default_factory=list)
    complaint_count: int = 0
    complaint_samples: list[str] = Field(default_factory=list, max_length=5)


class Incident(BaseModel):
    """A draft or confirmed incident flowing through n8n into the agent."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^inc-[a-z0-9-]{8,}$")
    created_at: datetime
    status: Literal["draft", "triaging", "suppressed", "rejected", "triaged", "review"]
    signal_ids: list[str] = Field(min_length=1)
    service: str
    environment: str
    p_level: Literal["P1", "P2", "P3", "P4"] | None = None  # None until triage assigns it
    started_at: datetime | None = None
    symptom: str = Field(min_length=1, max_length=1000)
    context: IncidentContext = Field(default_factory=IncidentContext)


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str            # corpus doc id or tool call id
    source_type: Literal["runbook", "incident_history", "service_doc", "tool_result"]
    quote: str = Field(max_length=500)


class TriageReport(BaseModel):
    """The one artifact PETER PAN produces. Output-guardrail-checked before routing."""
    model_config = ConfigDict(extra="forbid")

    incident_id: str
    category: Literal["infra", "database", "application"]   # drives n8n router node 8
    p_level: Literal["P1", "P2", "P3", "P4"]
    summary: str = Field(min_length=1, max_length=1200)
    probable_cause: str = Field(max_length=1200)
    citations: list[Citation] = Field(min_length=1)          # cited answers only — uncited = guardrail fail
    owner_team: str
    escalation_path: list[str] = Field(default_factory=list) # ordered roles, from Tools API only
    recommended_steps: list[str] = Field(default_factory=list, max_length=8)  # read-only/safe steps only
    confidence: float = Field(ge=0.0, le=1.0)
    guardrail_flags: list[str] = Field(default_factory=list) # non-empty → human review queue
    generated_at: datetime
    model_meta: dict[str, str] = Field(default_factory=dict) # provider, model id, fixture id in Stage A
```

**Deterministic-floor rules baked into the contracts** (per engineering principles): `owner_team`
and `escalation_path` may only be copied from Tools API responses — the LLM never invents them
(output guardrail verifies against the Tools API); `p_level` mapping from severity/impact is
deterministic code in the Predictor/Tools API, the LLM only proposes; `citations` non-empty is
schema-enforced.

**Seeds:** the four tool I/O schemas in `services/tools-api/schemas/*.json`
(recent_deployments, service_context, similar_incidents, escalation_preview) remain the tool-call
contracts; Stage A adds matching pydantic response models next to them.

## 2 · Packaging decision

Each `services/<name>/` is a self-contained deployment unit and **its own import root** (Docker
`WORKDIR`, per-service `pytest` rootdir): hyphenated dir name outside, snake_case package inside
(`services/tools-api/tools_api/…`). No `services.*` cross-imports ever — services communicate
over HTTP only. Consequence: Stage A restructures *within* each service dir (allowed) and never
moves files across service dirs again.

## 3 · Component inventory (mapped to diagram nodes)

### Layer 3 — EC2 microservices (`CORE` subgraph)

| component (node) | purpose | interface | deps | Stage A: real vs stubbed | tests |
|---|---|---|---|---|---|
| Ingestion API (`ING`) | accept signals, validate, normalize, forward | FastAPI `POST /signals` → `Signal`; `GET /healthz` | none (entry point) | **real** (it's just validation + forward to n8n webhook) | pytest: schema accept/reject table; contract round-trip |
| Predictive Engine (`PRED`) | anomaly detection on metric windows; draft-incident creation | FastAPI `POST /analyse` (metric window → score + draft `Incident`) | Prometheus query API (Stage A: fixture windows) | EWMA floor **real** (deterministic, unit-tested); PyTorch classifier **stubbed** (fixed weights fixture) | pytest: EWMA known-series table; classifier interface smoke |
| RAG Service (`RAG`) | cited answers over the corpus | FastAPI `POST /query` (question → answer + `Citation[]`) | corpus; LLM client (generation) | retrieval **real** via migrated TF-IDF stub (ADR 0001); generation via **mock LLM client**; refuses uncited answers (real logic) | migrated tests re-greened + golden-set retrieval eval (hit-rate) |
| Guardrails (`GRD`) | input/output checks | FastAPI `POST /check/input`, `POST /check/output` | Tools API (owner verification on output) | regex floor **real** (migrated); NeMo **stubbed** behind same interface; no-invented-owners check **real** | migrated test_guardrails re-greened + output-check table (invented owner, destructive step, uncited claim) |
| Tools API + approval gate (`TOOLS`) | owners · deploys · similar incidents · escalation · audit log | FastAPI, one route per tool matching `schemas/*.json`; `POST /escalations` preview-first; `GET /audit` | datasets in `data/`; escalation bridge | four tools **real** (migrated code, paths rewired); dispatch **stubbed** (preview-only; audit log to SQLite file) | 10 migrated test modules re-greened + approval-gate state tests |
| LangGraph agent (`LG`) | Planner → Specialists → Synthesiser triage brain | FastAPI `POST /agent/run` (`Incident` → `TriageReport`) | RAG, Tools API (HTTP); LLM client | graph topology **real** (LangGraph, deterministic routing); every LLM node via **mock client** | graph-path tests: P1 vs P3 fixtures walk expected node sequences; output always validates as `TriageReport` |

### Layer 2 — n8n orchestration (`N8N`, flow nodes 1–8)

| flow node | Stage A implementation | test |
|---|---|---|
| 1 Webhook trigger | n8n webhook receiving `Signal` from Ingestion/UI | curl fixture → 200 |
| 2/7 Guardrails in/out | HTTP nodes → `GRD /check/*` | flow run with failing fixture → rejection/review branch |
| 3/IF gates | n8n IF nodes on guardrail verdicts | covered by branch fixtures |
| CTX enrichment (MW/DEP/CMP → merge) | calendar check **stub** (static JSON); GitHub deployments **real API, fake repo**; Slack complaints **stub** (fixture) | merge output validates as `IncidentContext` |
| 4 Extractor | n8n LLM node → **mock endpoint** (Stage C: Bedrock Haiku) | extraction fixture → expected `Incident` fields |
| 5 Agent | HTTP → `LG /agent/run` | E2E fixture |
| 6 LLM Chain → TriageReport | Structured Output Parser with `TriageReport` JSON Schema | schema-reject fixture → review queue |
| 8 Router + team webhooks + Slack + P1 escalation | n8n switch on `category`+`p_level`; team webhooks = **webhook.site/stub URLs**; Slack channel **stubbed** in Stage A | routing table test: 4 fixtures → 4 destinations |

Flow JSON is exported to `/n8n/peter-flow.json` **on every change** and versioned.

### Layer 1 — UI (`HUM`, Stage B)

Streamlit WebUI (`UI`): incident submission form → n8n webhook; TriageReport viewer; local
assistant chat panel wired to the LLM client (Ollama in Stage C). Tests: Streamlit AppTest
(scripted session) + one Playwright smoke against the running stack.

### Layer 4 — AI models (`AI`, Stage C) — the single mockable seam

One interface, defined in Stage A and vendored like the contracts:

```python
class LLMClient(Protocol):
    def complete(self, *, task: Literal["extract", "agent", "synthesis", "rag_generate", "assistant"],
                 prompt: str, schema: dict | None = None) -> LLMResult: ...
```

Stage A ships only `FixtureLLMClient` (deterministic canned responses keyed by task + fixture id;
records prompts for assertion). Stage C adds `BedrockClient` (Sonnet: agent/synthesis, Haiku:
extract), `LlamaCppClient` (rag_generate), `OllamaClient` (assistant) — selected by env config.
**No service ever imports a provider SDK directly.**

### Knowledge & Comms seams (`KNOW`/`HUM`)

Confluence→pgvector ingestion (`CONF`→`PGV`) and Supabase pgvector are **Stage C** (RAG stub
needs neither); OpenClaw/Telegram approvals (`OC`) are **Stage C**, stubbed in Stage A as an
approval-gate REST endpoint; GitHub deploy events (`GH`) enter via the n8n context branch
(Stage A, against a fake repo); CI eval harness (`GH -.-> CORE`) lands in Stage A (`/evaluation`).

## 4 · Stages

### Stage A — Layers 2+3 together, mock-first

- **Scope boundary (explicitly NOT in Stage A):** Streamlit UI, any real LLM call, Bedrock/
  llama.cpp/Ollama wiring, Confluence sync, pgvector/Supabase, OpenClaw/Telegram, real Slack,
  the k3d demo environment (separate work item), the parked React frontend.
- **Inherited backlog (ADR 0001 limitations):** rewire `app.*` imports + path constants in all
  migrated modules; replace `lambda_root`/`BedrockError` dependencies; per-service packaging
  (§2); re-green all 15 migrated test modules; reconcile `evaluation/rag_evaluation_cases.json`
  cases 2–3 with the actual corpus; restore per-service CI test jobs.
- **Exit gate (verifiable):** `docker compose up` + one command
  (`evaluation/run_e2e.py`) posts the golden `Signal` fixtures to Ingestion and receives valid
  `TriageReport`s through the full n8n flow **with zero external API calls** (asserted: no
  network egress beyond compose network + n8n); `pytest` green in every service; CI green;
  `/n8n/peter-flow.json` current.
- **Git tag:** `v0.1-stage-a`.
- **Tests that must pass:** all `services/*/tests/`, contract-copy identity test, n8n routing
  fixtures, E2E golden path (≥ the 3 golden-set JSONs in `/evaluation`).

### Stage B — Layer 1 UI

- **Scope boundary (NOT):** real LLMs, React frontend revival, new endpoints (UI consumes only
  what Stage A shipped).
- **Exit gate:** manual incident submitted in Streamlit → TriageReport rendered back in the UI,
  against the mock-backed stack; Streamlit AppTest + Playwright smoke green.
- **Git tag:** `v0.2-stage-b`. **Tests:** Stage A suite + UI tests (no Stage A test may regress).

### Stage C — Layer 4 real providers, last

- **Scope boundary (NOT):** new features, flow changes, contract changes. One module per
  service: swap `FixtureLLMClient` for the real client via config.
- **Order within C:** Bedrock (Haiku extract → Sonnet agent/synthesis) → llama.cpp GGUF for RAG
  → Ollama assistant → Confluence→pgvector ingestion → OpenClaw approvals → real Slack.
- **Exit gate:** the same Stage A E2E suite green against real providers (fixtures replaced by
  recorded assertions with tolerance); eval harness scores (retrieval hit-rate, TriageReport
  schema-validity rate, guardrail catch rate) recorded in `/evaluation/results/`.
- **Git tag:** `v0.3-stage-c`. **Tests:** full suite + eval harness thresholds.

## 5 · Risk register (top 5)

| # | risk | mitigation |
|---|---|---|
| 1 | **Local-demo-env ↔ AWS seam** — k3d/Grafana runs locally, core runs on EC2; webhooks across NAT | Stage A runs *everything* in one local docker compose; the EC2 split is a deploy variant, not a code path. Grafana→Ingestion is plain HTTP with a shared-secret header; demo env can replay recorded alert fixtures if the live link fails. |
| 2 | **n8n webhook reachability** (EC2 security groups, n8n auth, URL drift) | webhook URL + auth from env only; `run_e2e.py` asserts reachability as its first step; exported flow JSON keeps credentials as placeholders. |
| 3 | **Bedrock quota/cost** (Stage C) | mock-first design means Bedrock appears only in Stage C behind `LLMClient`; per-task model routing (Haiku for extraction) caps cost; retries with backoff + a hard daily budget env var; demo can always fall back to fixtures. |
| 4 | **GGUF memory on the EC2 instance** (Mistral 7B + n8n + 6 services) | quantized Q4 model, llama.cpp server with capped context; RAG generation is optional-per-request — TF-IDF+extractive fallback stays wired; measure RSS in Stage C exit gate before demo day. |
| 5 | **Scope drift** (reviving the React frontend, adding non-diagram components) | every PR checked against the diagrams; frontend/ excluded from CI and the plan; stage scope-boundary lists are the review checklist; one phase per approval (standing rule). |

## 6 · Effort honesty (> 2–3 sessions flagged)

- **Stage A as a whole is ~4–6 sessions**, not 2–3: import/path rewiring + re-greening 15 test
  modules (~1), Tools API + Guardrails + RAG services (~1–2), LangGraph agent + mock client
  (~1), n8n flow + E2E harness (~1–2). Flagged.
- **Demo environment (k3d + OTel + Prometheus/Loki/Grafana + chaos injector)** is its own
  2–4 session project and is *not* required for the Stage A exit gate (fixtures suffice). Flagged.
- **Predictor's PyTorch classifier training** is unbounded if allowed; Stage A ships the EWMA
  floor + a stub classifier, training is a Stage C-adjacent stretch goal. Flagged.
- Stage B (~1–2 sessions) and Stage C Bedrock+Ollama (~1–2 sessions) fit the budget; llama.cpp
  on EC2 may spill (see risk 4).

## 7 · Conflicts (listed, not silently resolved)

1–5. Carried from [ADR 0001](adr/0001-piter-carryover.md) (diagrams' original location, no
pydantic in PITER, tool-name mapping, parked frontend vs Streamlit, local `main` revert).
6. **Diagram vs task wording:** the n8n flow's agent node (5) says "Bedrock Claude Sonnet · tool
calls" while node T3 calls the LangGraph agent service — i.e., *two* agent brains (n8n AI-Agent
node and LangGraph service). This plan treats the n8n node 5 as the orchestrating caller and
LangGraph as *the* triage brain (per system diagram "N8N →|triage brain| LG"); if you intended
the n8n AI-Agent node to do independent tool-calling with Bedrock, say so and Stage A's node-5
wiring changes.
7. `evaluation/rag_evaluation_cases.json` expects two corpus docs that don't exist post-reset
(ADR limitation 6) — reconciled when the eval harness is built, direction needs a call: restore
equivalent docs to the corpus, or rewrite the cases.
