# PETER PAN — Final Project Plan & Guideline Crosswalk

> **Audience:** course instructor and reviewers.
> **Claim:** PETER PAN is a 1:1 crosswalk of the *AI Property Triage System* final-project guideline
> into the incident-operations (AIOps) domain — every graded capability, every rubric line, and every
> deliverable is preserved; only the domain and three declared technology choices differ, and each
> difference is justified below the way it would be defended in an enterprise design review.
>
> Companion documents: [BUILD_PLAN.md](BUILD_PLAN.md) (internal execution plan),
> [ARCHITECTURE.md](ARCHITECTURE.md) (runtime flow, service status, health commands),
> [ADR 0002](adr/0002-model-memory-db.md) (models / memory / storage),
> [ADR 0003](adr/0003-system-boundaries.md) (system boundaries),
> [peter-pan-system.mmd](peter-pan-system.mmd) + [peter-pan-n8n-flow.mmd](peter-pan-n8n-flow.mmd)
> (our own annotated architecture diagrams — deliverable §7.2).

> **Implementation status (2026-07-11):** this document is the target/rubric crosswalk,
> not a completion report. Stage A uses deterministic fixture seams, and its seven-scenario
> Ingestion → n8n → routed TriageReport gate is verified. PyTorch
> training, the 55+ document corpus, prompt-log evidence, real model providers, presentation
> media, and AWS deployment remain planned. Current evidence is tracked in
> [ARCHITECTURE.md](ARCHITECTURE.md) and [the end-to-end audit](audits/2026-07-10-end-to-end-audit.md).

**PETER** = Priority · Enrichment · Triage · Escalation · Resolution
**PAN** = Predictive · Agentic · Navigator

---



## 1 · Executive summary

The guideline automates real-estate listing intake: validate → extract → classify images → retrieve
similar listings → route → publish a structured brief. PETER PAN automates **incident intake and
triage** for an SRE organisation: validate the signal → extract incident fields → classify metric
windows → retrieve similar incidents and runbooks → route to the owning team → publish a structured
triage report. The pipeline shape, the four-layer architecture, the n8n 8-node spine, the four core
FastAPI services, the five graded prompt surfaces, and the rubric metrics are identical.

Why change the domain at all? The author works in production operations in a regulated,
multi-jurisdiction environment. Building the *same graded system* on a domain with real operational
stakes produces a portfolio piece that is defensible in an interview — which is exactly what the
guideline's closing line asks for. Nothing graded is lost: the crosswalk below maps every
requirement to its PETER PAN equivalent, line by line.

**Three declared deviations** (per guideline §7.2, which explicitly requires documenting
"any deviations from the specification"):


| #   | Guideline                                    | PETER PAN                                                                   | Nature of change                                                                                                                                       |
| --- | -------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| D-1 | Real-estate listing intake                   | AIOps incident triage                                                       | Domain swap; all capabilities preserved                                                                                                                |
| D-2 | Image classifier (room type + condition 1–5) | Time-series classifier (incident category + severity 1–5) on metric windows | Modality swap; same PyTorch dual-head architecture, training loop, dataset, accuracy target, uncertainty handling. Vision fallback documented (§5.3.2) |
| D-3 | GPT-4o (agent LM) · ChromaDB only            | Optional Stage C Bedrock/Gemini · pgvector alongside ChromaDB               | One-node / one-config swaps, both reversible; rationale in §6 (D5, D6)                                                                                 |


---



## 2 · Domain translation — the crosswalk dictionary

Every noun in the guideline has exactly one PETER PAN counterpart:


| Guideline (real estate)                                          | PETER PAN (AIOps)                                                                                                              |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Property submission (text + images)                              | Incident **Signal** (Grafana alert · manual report · deploy event · complaint)                                                 |
| Listing agent                                                    | On-call engineer / reporter                                                                                                    |
| Spam / off-topic submission                                      | Non-incident noise, spam, prompt injection                                                                                     |
| Property type · location · price · rooms · certifications        | Service · environment · symptom · severity hint · start time                                                                   |
| Property **images**                                              | **Metric windows** (CPU, memory, DB, error-rate time series)                                                                   |
| 6 room types (kitchen … other)                                   | 6 incident categories (`cpu_saturation`, `memory_leak`, `db_lock_contention`, `replication_lag`, `error_rate_spike`, `normal`) |
| Condition score 1–5                                              | Severity 1–5 → priority P4–P1                                                                                                  |
| Similar past listings (internal KB)                              | Similar past incidents + runbook references                                                                                    |
| Residential / Commercial routing                                 | `infra` / `database` / `application` category routing **+ P-level escalation**                                                 |
| Publish-ready listing brief                                      | **TriageReport** (typed, schema-enforced)                                                                                      |
| False legal claims · invented prices · fabricated certifications | Invented owner teams · invented escalation paths · destructive remediation commands · uncited claims                           |
| Real-estate assistant (Ollama)                                   | SRE assistant (Ollama)                                                                                                         |


The intake pipeline maps step-for-step:

1. Validate genuine listing → validate genuine incident signal (Guardrails in)
2. Extract fields from text → extract incident fields (Stage A FixtureLM; optional Stage C Gemini)
3. Classify images → classify metric windows (Predictor, PyTorch dual head)
4. Retrieve similar listings → retrieve similar incidents + runbooks (RAG)
5. Route residential/commercial → route by category + priority (n8n Router)
6. Publish structured brief → publish `TriageReport` (LLM Chain + Structured Output Parser)

---



## 3 · Learning objectives coverage (guideline §1.2)

> **Stage A in progress.** Items marked *(planned)* are committed rubric work, not yet
> implemented. See [ARCHITECTURE.md](ARCHITECTURE.md) for the current implemented/stubbed/planned
> breakdown.


| #   | Objective                                  | Where satisfied                                                                                         |
| --- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| 1   | Multi-service AI system on AWS EC2         | 6 Dockerized FastAPI services, single EC2 t3.large, docker-compose (§12) *(EC2 deploy: Stage C)*       |
| 2   | n8n flows with AI Agent nodes + HTTP calls | 8-node spine, `n8n/peter-flow.json`, exported & versioned on every change (§5.2)                       |
| 3   | RAG with LangChain + Llama.cpp + vector DB | RAG service: TF-IDF retrieval implemented; llama.cpp GGUF + pgvector *(Stage C)*                       |
| 4   | Write **and train** a PyTorch classifier   | Predictor: EWMA floor implemented; 1D-CNN/GRU + training + ≥200-sample dataset *(Stage C)*             |
| 5   | Prompt engineering across ≥5 components    | 5 official surfaces + 2 appendix surfaces, 5 iterations each, frozen test sets *(Stage A → C)*         |
| 6   | NeMo Guardrails or custom rule engine      | Regex floor implemented; NeMo layer *(stubbed — Stage C)*                                               |
| 7   | LangGraph multi-step agent                 | Planner → Tools → Synthesiser, stateful, `POST /agent/run` (§5.3.4)                                    |
| 8   | Local Ollama + conversational web UI       | Streamlit skeleton exists; Ollama wiring + WebUI tabs *(Stage B / Stage C)*                             |


---



## 4 · Architecture at a glance

Four layers, HTTP between them — identical topology to the guideline's Figure 1:

```
Layer 1  UI            Streamlit: SRE assistant (optional Stage C Ollama) · incident submission · monitoring tab (ext.)
Layer 2  Orchestration  n8n 8-node spine + context-enrichment branches
Layer 3  Services       6 FastAPI microservices on EC2 (Docker, non-root)
Layer 4  Models         Optional Stage C: Gemini Flash · Bedrock Claude Sonnet · llama.cpp GGUF · Ollama
```

Our own annotated diagrams (guideline deliverable: *"your own version, not a copy of Figure 1"*):
[peter-pan-system.mmd](peter-pan-system.mmd) and [peter-pan-n8n-flow.mmd](peter-pan-n8n-flow.mmd).

---



## 5 · Layer-by-layer plan



### 5.1 Layer 1 — WebUI (guideline §5)

Streamlit (chosen over Gradio: better multi-tab layout control, native session state for the
review-queue extension, `AppTest` gives scriptable UI tests in plain pytest).


| Tab                      | Guideline requirement                                                                                                              | PETER PAN implementation                                                                                                                                                                                                                                 |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Assistant                | Chat → local Ollama (Llama 3/Mistral), grounded real-estate assistant, polite off-topic refusal, no invented prices / legal advice | Stage B fixture-backed SRE assistant; optional Stage C local Ollama. Refuses off-topic and destructive-action requests. Prompt surface #5 (§7) |
| Submission               | Description + image URLs + agent name → POST n8n webhook; renders returned report incl. image scores + similar listings            | Incident description + metric-window reference + reporter → POST n8n webhook; renders `TriageReport` incl. predictor category/severity + similar incidents/runbooks                                                                                      |
| Monitoring *(extension)* | Optional third tab (§10)                                                                                                           | Signals processed, guardrail hit-rate, avg severity, avg flow execution time, last-10 events — fed from the Tools API audit log (§11.4)                                                                                                                  |




### 5.2 Layer 2 — n8n flow (guideline §3, node-for-node)

Already built as `n8n/peter-flow.json`; the export is refreshed and versioned on every change
(guideline deliverable §7.1).


| Node                   | Guideline                                                                                                               | PETER PAN                                                                                                                                                                                                             |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 Webhook              | Form POST: description + image URLs                                                                                     | `Signal` JSON from Ingestion API / UI                                                                                                                                                                                 |
| 2 Guardrails in        | HTTP → `/check/input`, pass/fail                                                                                        | Same endpoint, same contract                                                                                                                                                                                          |
| 3 IF                   | fail → rejection + error message                                                                                        | fail → rejection; verdict logged to audit trail                                                                                                                                                                       |
| — CTX *(our addition)* | —                                                                                                                       | Parallel enrichment: maintenance-window check · recent deploys (GitHub) · complaint correlation (Slack) → merged `IncidentContext`. Rationale: §6 D4                                                                  |
| 4 Extractor            | Gemini LM node; type/location/price/rooms/certs; facts-only, graceful nulls, typed                                      | Stage A FixtureLM; optional Stage C Gemini 2.5 Flash. Extracts service/environment/symptom/start-time. **Prompt surface #1**                                                                                                     |
| 5 AI Agent             | GPT-4o/Gemini; role "senior property analyst"; tool calls → RAG, Image Analyser, LangGraph                              | Stage A FixtureLM; optional Stage C Bedrock Claude Sonnet. Role **"senior SRE incident commander"**; tools → RAG, **Predictor**, LangGraph (+ Tools API facts). **Prompt surface #2**                                                                     |
| 6 LLM Chain            | Synthesise 3 sources (fields, image scores, RAG context) into brief; Structured Output Parser JSON schema; no invention | Synthesise extracted fields + predictor scores + RAG context into `TriageReport`; Structured Output Parser carries the `TriageReport` JSON Schema exported from the pydantic contract. *(Appendix prompt surface A1)* |
| 7 Guardrails out       | No false legal claims / prices / fabricated certs; fail → human review                                                  | No invented owners/escalation paths (**verified against Tools API ground truth**), no destructive steps, no uncited claims; fail → review queue                                                                       |
| 8 Router               | `property_type` → residential / commercial webhooks                                                                     | `category` → infra / database / application team webhooks **+ P1 escalation branch** — a superset of the graded binary router                                                                                         |


Parallel dispatch requirement: the agent's tool calls and the CTX branches run as parallel HTTP
requests merged before node 6 — the rubric's "parallel EC2 calls wired correctly" line.

### 5.3 Layer 3 — EC2 microservices (guideline §4)

Guideline requires four services; PETER PAN ships **six** (§6 D3 justifies the two additions).
Each lives in `services/<name>/` with its own Dockerfile, requirements, tests, and import root —
services communicate over HTTP only, never cross-imports.

#### 5.3.1 RAG service (`services/rag/`) — guideline §4.1


|               | Guideline                                                                       | PETER PAN                                                                                                                                          |
| ------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Endpoint      | `POST /query` `{description}`                                                   | Same                                                                                                                                               |
| Output        | `{similar_listings, insight}`                                                   | `{similar_incidents, runbook_refs, insight}` — same shape + runbook refs                                                                           |
| Pipeline      | sentence-transformer embed → ChromaDB top-3 → LangChain prompt → llama.cpp GGUF | Stage A TF-IDF + extractive cited answers; optional Stage C embeddings, pgvector, and llama.cpp generation |
| Corpus        | ≥20 synthetic listings pre-seeded                                               | **≥55 synthetic incidents/runbooks/service docs** via `scripts/seed_kb.py` (Stage A)                                                               |
| Citation rule | Prompt-instructed: cite source listing, no fabrication                          | Prompt-instructed **and code-enforced**: uncited answers are refused; `TriageReport.citations` is schema-required non-empty. **Prompt surface #3** |




#### 5.3.2 Image Analyser → Predictive Engine (`services/predictor/`) — guideline §4.2, deviation D-2

The rubric grades: a trained PyTorch dual-head classifier, ≥200-sample self-built dataset,
own training loop, >75 % test accuracy, graceful uncertainty. All preserved:


|             | Guideline                                  | PETER PAN                                                                                                                                                                                                                                                                                       |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Endpoint    | `POST /analyse` `{image_url}`              | `POST /analyse` `{metric_window_ref}`                                                                                                                                                                                                                                                           |
| Output      | `{room_type, condition_score, confidence}` | `{category, severity, confidence}`                                                                                                                                                                                                                                                              |
| Classes     | 6 room types                               | 6 incident categories                                                                                                                                                                                                                                                                           |
| Second head | condition 1–5                              | severity 1–5 → deterministic P4–P1 mapping                                                                                                                                                                                                                                                      |
| Dataset     | ≥200 labelled images, sourced/synthesised  | ≥200 labelled synthetic metric windows via `predictive/datagen` — **train/test generated with disjoint seeds and parameter ranges** so the accuracy number is honest, not leakage                                                                                                               |
| Training    | Transfer-learn ResNet-50/EfficientNet head | 1D-CNN/GRU trained **from scratch** — no pre-trained backbone exists for arbitrary metric windows; the network is small enough that scratch training is the correct engineering call. Documented augmentation (noise, scaling, window jitter) + test accuracy reported in `evaluation/results/` |
| Uncertainty | Confidence threshold → "uncertain" label   | Same threshold **plus a deterministic EWMA/z-score floor**: a statistical anomaly detector that fires independently of the model, so a real anomaly is never silenced by model failure (§6 D1)                                                                                                  |
| Honest note | —                                          | If literal image input is required for the rubric line, the documented fallback renders metric windows as chart images and classifies those through a fine-tuned ResNet — one preprocessing step, same service contract                                                                         |




#### 5.3.3 Guardrails service (`services/guardrails/`) — guideline §4.3


|             | Guideline                                                           | PETER PAN                                                                                                                                                                                                                                                                                                                                |
| ----------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Endpoints   | `POST /check/input` · `POST /check/output`                          | Same                                                                                                                                                                                                                                                                                                                                     |
| Output      | `{pass, reason, safe_text}`                                         | Stage A `{pass, flags, reason}` with deterministic fail-closed checks |
| Input rail  | Genuine listing, expected language, reject spam/offensive/off-topic | Genuine incident signal; rejects spam, off-topic, offensive content, prompt injection                                                                                                                                                                                                                                                    |
| Output rail | No false legal claims / invented prices / fabricated certifications | No invented owner teams or escalation paths — **verified against the Tools API, a deterministic ground truth** — no destructive commands, no uncited claims                                                                                                                                                                              |
| Engine      | NeMo Guardrails, YAML/Colang                                        | **Two-tier**: deterministic regex/rule floor (always on, unit-tested, fail-closed) + NeMo rails above it. The guideline offers "NeMo *or* custom rule engine"; we build both because an LLM should never be the only thing between a bad output and production (§6 D1). **Prompt surface #4** (topic-detection + output-auditor prompts) |




#### 5.3.4 LangGraph agent (`services/langgraph-agent/`) — guideline §4.4


|               | Guideline                                                              | PETER PAN                                                                                                                                                                                                    |
| ------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Endpoint      | `POST /agent/run` `{query}` → `{answer, tools_used, reasoning_steps}`  | `POST /agent/run` `{incident, question?}` → canonical `TriageReport` |
| Graph         | Planner → tool executor (RAG + Image tools) → Synthesiser, stateful    | Planner → parallel RAG + Tools API specialists → Synthesiser; n8n owns the separate Predictor call |
| Example query | "What renovation brings this to condition 5?"                          | "What remediation returns this service to healthy? Which components need attention first?"                                                                                                                   |
| Benchmark     | Tool descriptions iterated ≥5×, same 10 benchmark queries each version | `evaluation/tool_evaluation_cases.json` (already in repo) is the frozen 10-query benchmark; test sets are never mutated mid-run. *(Appendix prompt surface A2)*                                              |




#### 5.3.5 The two additional services (beyond the required four)


| Service                                               | Purpose                                                                                         | Enterprise rationale                                                                                                                                                                                                                                                                  |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ingestion API** (`services/ingestion/`)             | `POST /signals`: validate + normalise every inbound signal before it reaches the orchestrator   | Fail fast at the boundary. The guideline's webhook parses raw JSON inside the flow; validating *before* orchestration means malformed input can never corrupt a mid-flow state. Standard API-gateway pattern                                                                          |
| **Tools API + approval gate** (`services/tools-api/`) | Owners · deployments · similar incidents · escalation **preview-first** · append-only audit log | Gives the LLM a deterministic source of truth to cite and the output guardrail a ground truth to verify against. Escalations are preview-only until a human approves — the "LLM proposes, deterministic layer disposes" pattern. The audit log also feeds the monitoring tab for free |


All six expose `GET /healthz`. Before any demo, run:
```powershell
python scripts/run_all_tests.py   # all service pytest suites
docker compose config --quiet     # compose syntax check
python evaluation/run_e2e.py --dry-run  # fixture load, no HTTP
```
The full compose-backed E2E (Ingestion → n8n → TriageReport) is the Stage A exit gate.

### 5.4 Layer 4 — model routing (guideline §8)

One protocol seam, defined before any real provider is wired
(`LLMClient` — no service ever imports a provider SDK directly):


| Task                              | Guideline                      | PETER PAN                                                                            | Why                                                                                                             |
| --------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| n8n extraction (node 4)           | Gemini                         | Stage A FixtureLM; optional Stage C **Gemini 2.5 Flash**                             | Fast, cheap, strong structured extraction, native n8n LM node                                                   |
| n8n agent + synthesis (nodes 5–6) | GPT-4o or Gemini               | Stage A FixtureLM; optional Stage C **AWS Bedrock Claude Sonnet**                    | §6 D5                                                                                                           |
| RAG generation                    | llama.cpp + GGUF on EBS        | Stage A extractive retrieval; optional Stage C llama.cpp GGUF                        | Current cited retrieval is deterministic; local generation remains a later provider swap                       |
| WebUI assistant                   | Local Ollama (Llama 3/Mistral) | Stage B fixture; optional Stage C Ollama                                              | Local-first privacy; no API cost for a chat surface                                                             |
| Development / CI                  | —                              | **FixtureLLMClient**: deterministic canned responses, records prompts for assertions | The whole pipeline is testable with **zero external API calls** — CI never depends on a vendor being up (§6 D2) |


Two independent cloud providers (Google + AWS) plus two local runtimes behind one interface —
provider-agnostic by construction, each swap is one config value.

---



## 6 · Engineering decision log — the "why", as an enterprise review would hear it

**D1 — Deterministic floors under every model.**
Regex rules under NeMo; EWMA/z-score under the classifier; P-level mapping in code;
`owner_team`/`escalation_path` copyable only from Tools API responses; citations schema-required.
*Why:* in production (and in regulated environments) an LLM is never the last line of defence.
Models decide only at extraction/generation steps; business, scoring, and threshold logic stays
deterministic and unit-tested. This directly strengthens two rubric lines: guardrails FP-rate
(the floor is measurable and stable) and "handles error cases" (fail-closed by default).

**D2 — Mock-first build order behind a single LLM seam.**
Stage A builds Layers 2+3 end-to-end against `FixtureLLMClient`; real providers arrive last
(Stage C) as config swaps. *Why:* the 45 % of the grade that is "flow + services" is proven
green before a single API dollar is spent; demos can always fall back to fixtures; CI is
deterministic. This is the guideline's §11.2 local-first order, made a hard gate rather than advice.

**D3 — Six services instead of four.**
The four graded services are preserved 1:1; Ingestion API and Tools API are added (§5.3.5).
*Why:* boundary validation and a deterministic tool/audit layer are what make the guardrails and
agent stories *provable* instead of asserted. Cost: two more small containers on the same box.

**D4 — Context-enrichment branches in n8n (maintenance window · recent deploys · complaints).**
*Why:* the "E" in PETER is Enrichment — triage quality depends on evidence ("deploy 12 min before
the alert") rather than model intuition. It also exercises exactly the graded n8n skill: parallel
HTTP branches merged mid-flow.

**D5 — Bedrock Claude Sonnet instead of GPT-4o for the agent/synthesis nodes.**
This is an optional Stage C provider decision, not a dependency of the Layers 2–3 exit gate.
*Why:* (a) the system already runs on AWS — Bedrock access is IAM-scoped, keeps inference inside
the same cloud account, and eliminates a second API-key secret to manage; (b) strong tool-use and
structured-output behaviour, which is what nodes 5–6 grade; (c) per-task routing (Flash for
extraction, Sonnet only where reasoning matters) caps cost with a hard daily budget env var;
(d) it is a one-node swap in n8n — reversible in minutes if the instructor prefers the reference
stack. Declared as deviation D-3.

**D6 — pgvector (Supabase/Postgres) alongside ChromaDB.**
*Why:* ChromaDB stays for guideline parity; pgvector is the *managed vector store* extension the
guideline itself proposes (§10.3) — chosen over Pinecone/Weaviate because Postgres is already in
the stack, incident metadata is SQL-joinable with embeddings (one query for "similar incidents in
the same service"), and it adds no new vendor or secret. The required precision@3 before/after
benchmark is part of the extension deliverable (§11.3).

**D7 — Streamlit over Gradio.** Multi-tab layout, session state for the review queue, and
`AppTest` for scriptable UI tests. Either satisfies the rubric; this one is more testable.

**D8 — Single EC2 t3.large + docker-compose instead of per-service** `docker run`**.**
*Why:* one command brings up the entire graded stack (`docker compose up`), with restart policies,
one private network, and per-container resource caps; one instance is the honest cost envelope for
a ≤5-user portfolio demo. The guideline's checklist (§11.3) is satisfied verbatim — including its
security note: inbound restricted to the n8n egress IP + dev IP, **never 0.0.0.0/0**; containers
run non-root; GGUF on EBS.

**D9 — Contracts frozen first.** `Signal`, `Incident`, `TriageReport` (pydantic v2,
`extra="forbid"`) are frozen at Stage A start; the `TriageReport` JSON Schema is exported into the
n8n Structured Output Parser so Layer 2 and Layer 3 cannot drift apart. Changing a contract
requires an ADR. *Why:* "endpoints return correct schema" is worth 25 % — schema correctness is
enforced by construction, not by hope.

**D10 — Frozen evaluation sets + results as artifacts.** Test sets in `/evaluation` are never
mutated mid-run; every rubric metric (accuracy, FP-rate, prompt pass-rates, E2E schema validity)
is measured by `evaluation/run_e2e.py` + per-surface suites and recorded in `evaluation/results/`.
*Why:* every graded number in this document is reproducible by the grader with one command.

---



## 7 · Prompt Engineering Log — 25 % of the grade (guideline §6)

The five official surfaces, logged in the exact required format
(V1 baseline → V2–3 targeted failure fixes → V4–5 refinement + learnings → final entry with
per-decision justification and pass rate on ≥10 frozen test cases):


| #   | Surface                            | PETER PAN prompt                                                                            | Frozen test set                                                                   |
| --- | ---------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| 1   | n8n Information Extractor (node 4) | Incident-field extraction `systemPromptTemplate` — facts-only, graceful nulls, typed output | ≥10 signal fixtures incl. missing-field and ambiguous cases                       |
| 2   | n8n AI Agent (node 5)              | "Senior SRE incident commander" system prompt + tool descriptions                           | ≥10 incidents requiring different tool sequences                                  |
| 3   | RAG retrieval/generation           | Context-injection + citation instructions for llama.cpp                                     | `evaluation/rag_evaluation_cases.json`                                            |
| 4   | Guardrails rails                   | Topic-detection prompt + output-auditor prompt (≥5 iterations **each**)                     | Valid/invalid signal sets → FP/FN rates                                           |
| 5   | Ollama assistant                   | SRE-assistant grounding + refusal behaviour                                                 | ≥10 edge cases: off-topic, destructive-command requests, prompt-override attempts |


**Appendix surfaces** (prompt tasks named in guideline §§3–4 but outside the graded log table —
logged anyway, same format, as low-cost completeness):
**A1** node 6 LLM-Chain synthesis prompt · **A2** LangGraph tool descriptions
(benchmarked against the frozen 10 queries in `evaluation/tool_evaluation_cases.json`).

Per CLAUDE.md, the log grows from Phase 2 onward — iterations are recorded as they happen, never
reconstructed after the fact. Each version's pass rate comes from re-running the frozen set, so
"measurable improvement demonstrated" (the Excellent-band phrase) is a table of numbers, not prose.

---



## 8 · Rubric alignment — targets and where they're measured


| Criterion      | Weight | Excellent-band bar                                                     | PETER PAN target & measurement                                                                                                                                                                  |
| -------------- | ------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| n8n Flow       | 20 %   | All nodes, guardrails integrated, router works, parallel calls correct | 8 nodes + CTX branches; routing table test (4 fixtures → 4 destinations); flow JSON versioned; E2E via `evaluation/run_e2e.py`                                                                  |
| EC2 Services   | 25 %   | All four deployed, Dockerized, correct schema, error cases             | Six services, typed pydantic contracts (`extra="forbid"`), fail-safe paths, `/healthz` on all, per-service pytest + CI; deployed on EC2 for the graded demo (explicit fail condition otherwise) |
| Image Analyser | 10 %   | Trained, >75 % test accuracy, graceful uncertainty                     | Predictor: **>75 %** on a disjoint-seed synthetic test set, reported in `evaluation/results/`; confidence threshold → uncertain path; EWMA floor as independent backstop                        |
| Guardrails     | 10 %   | Both rails, well-designed configs, <5 % FP on valid inputs             | **<5 % FP** measured on the frozen valid-signal set in CI; regex floor keeps the number stable across model/prompt changes                                                                      |
| Prompt Log     | 25 %   | 5 surfaces × 5 iterations, failure analysis, measurable improvement    | §7: 5 + 2 surfaces, per-version pass rates on frozen sets                                                                                                                                       |
| WebUI + Ollama | 10 %   | Both tabs functional, tuned prompt, report displayed                   | Stage B exit gate: submission → rendered TriageReport; Streamlit AppTest + Playwright smoke                                                                                                     |


---



## 9 · Deliverables mapping (guideline §7)


| Deliverable                                                    | PETER PAN artifact                                                                                                                                                                                        |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| n8n flow JSON (importable)                                     | `n8n/peter-flow.json` — re-exported on every change                                                                                                                                                       |
| Four service dirs, each with Dockerfile + requirements         | `services/{ingestion,predictor,rag,guardrails,tools-api,langgraph-agent}/` — six, each self-contained                                                                                                     |
| WebUI source + local-run README                                | `ui/` (Stage B) + README                                                                                                                                                                                  |
| Vector-store seeding script (≥20 docs)                         | `scripts/seed_kb.py` (Stage A) — ≥55 synthetic docs                                                                                                                                                       |
| PyTorch checkpoint **or** training script + repro instructions | Both: `.pth` checkpoint **and** `predictive/datagen` + training script with seeds pinned                                                                                                                  |
| Prompt Engineering Log (PDF/DOCX)                              | §7 logs, exported to PDF                                                                                                                                                                                  |
| Own annotated architecture diagram                             | `docs/peter-pan-system.mmd` + `docs/peter-pan-n8n-flow.mmd`, annotations = the decision log (§6)                                                                                                          |
| Deployment notes incl. deviations                              | `docs/deployment.md` + §1/§6 of this document                                                                                                                                                             |
| 5–8 min demo video, four scenarios                             | Storyboard: ① golden `Signal` → full `TriageReport` E2E ② spam/off-topic signal → node-3 rejection ③ invented-owner report → output rail → review queue ④ Ollama SRE-assistant exchange incl. one refusal |
| ZIP: `/code` `/docs` `/demo` + README                          | Assembled from the repo at tag time; top-level README carries setup/run                                                                                                                                   |


---



## 10 · Build order & milestones

Follows the guideline's §11.2 local-first order, hardened into staged gates
(full detail in [BUILD_PLAN.md](BUILD_PLAN.md)):


| Stage | Scope                                                                                                                                | Exit gate                                                                                                                                                                               | Tag            |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| **A** | Layers 2+3, mock-first (n8n spine built first against mock endpoints; all six services; fixture LLM; frozen contracts; eval harness) | `docker compose up` + `evaluation/run_e2e.py` posts golden signals → valid `TriageReport`s through the full flow with **zero external API calls**; all service pytest suites + CI green | `v0.1-stage-a` |
| **B** | Layer 1 Streamlit UI (both tabs + report rendering)                                                                                  | Manual submission in UI → TriageReport rendered back; AppTest + Playwright smoke green; no Stage A regression                                                                           | `v0.2-stage-b` |
| **C** | Layer 4 real providers (Gemini → Bedrock → llama.cpp → Ollama), pgvector ingestion, real Slack, extensions                           | Same Stage A E2E suite green against real providers; rubric metrics recorded in `evaluation/results/`; EC2 deployment live for the graded demo                                          | `v0.3-stage-c` |


---



## 11 · Optional extensions (guideline §10) — all four planned


| Ext.                                 | Guideline                                                                       | PETER PAN take                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------ | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 11.1 Feedback loop / active learning | Review queue + annotation + periodic classifier retrain                         | The review queue **already exists structurally** (output-rail failures → `status: "review"` + `guardrail_flags`). Add: reviewer tab marks reports correct/incorrect; annotations append to the predictor dataset; a retrain script re-fits and re-reports test accuracy. Clean active-learning loop because the dataset is synthetic-first |
| 11.2 Multilingual guardrail          | Detect unexpected languages (Hebrew or English), localised polite rejection     | Natural fit — the author is bilingual. Deterministic first tier: Unicode-script detection (Hebrew block) in the regex floor, no model needed; localised rejection messages in Hebrew and English. Accepted languages: en + he                                                                                                              |
| 11.3 Managed vector store            | Pinecone/Weaviate; benchmark precision@3 before/after                           | **Supabase pgvector** as the managed store (rationale §6 D6) — this converts declared deviation D-3 into the extension deliverable. Benchmark: precision@3 on `evaluation/rag_evaluation_cases.json`, ChromaDB vs pgvector, results in `evaluation/results/`                                                                               |
| 11.4 Monitoring dashboard            | Third tab: counts, guardrail hit-rate, avg score, avg exec time, last-10 events | Home turf for an SRE. All five stats derive from the Tools API append-only audit log — zero new infrastructure. Avg n8n execution time read via the n8n API                                                                                                                                                                                |


Extensions are strictly post-`v0.2`: none may delay a graded component (scope guard).

---



## 12 · Deployment & security (guideline §11)

Checklist parity, then hardening on top:

- **Instance:** single EC2 **t3.large** (guideline: "t3.large recommended for GPU-less inference") — all six services + n8n via docker-compose; GGUF quantised Q4 on EBS with capped llama.cpp context.
- **Security group:** inbound restricted to the n8n egress IP + the development machine IP — the guideline's own security note ("never 0.0.0.0/0") is a hard rule here, not a recommendation.
- **Containers:** non-root, pinned base images, per-container memory caps.
- **Secrets:** `.env` + AWS Secrets Manager; `.env.example` stays key-less; nothing sensitive in the repo or in the exported flow JSON (credentials exported as placeholders). Bedrock via IAM role, not long-lived keys.
- **Data:** synthetic only — no real PII, no real incidents, ever (repo golden rule).
- **Failure model:** portfolio scope — graceful degradation + recoverable restart (`restart: unless-stopped`), designed for ≤5 concurrent users, ≤1 signal/sec, ≤10k KB docs. The production path (multi-instance, LB, managed Postgres) is *documented* in `docs/deployment.md` but deliberately not built — matching scope to requirements is presented as a feature of the design, not a shortcut.

---



## 13 · Top risks & mitigations (abridged — full register in BUILD_PLAN §5)


| Risk                                   | Mitigation                                                                                                                 |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Bedrock quota/cost during Stage C      | Mock-first seam means providers arrive last; per-task routing; hard daily budget env var; fixture fallback for demos       |
| GGUF memory pressure on t3.large       | Q4 quant, capped context, RAG generation optional-per-request with extractive fallback; RSS measured at Stage C exit gate  |
| Synthetic-data accuracy looks inflated | Disjoint-seed train/test generation, stated openly in the training report                                                  |
| n8n webhook reachability on EC2        | URL + auth from env only; `run_e2e.py` asserts reachability first; flow JSON keeps credential placeholders                 |
| Scope drift (extensions before core)   | Extensions gated behind `v0.2`; every PR checked against the diagrams; stage scope-boundary lists are the review checklist |


---

*PETER PAN — built to be shown in an interview, which is exactly what the guideline asked for.*