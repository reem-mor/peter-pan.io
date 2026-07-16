# PETER PAN — Master Requirements & Build Checklist

The single source of truth that maps **every** requirement of the *AI Engineering Final
Project* guideline onto PETER PAN (AIOps incident triage). Same rubric lines, same
deliverables, domain-swapped from real estate to incident response. Work top-to-bottom;
tick boxes as you go.

> Domain swap is declared (§11). The grader scores **capabilities**, not the real-estate
> story — every capability is delivered 1:1 below.

Status: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` at risk

---

## 0. How to drive this with Cursor + Claude Code

The workflow that makes the AI maximally useful here — repeat per rubric line:

1. **Point the agent at this doc + the matching skill.** e.g. "Read `docs/MASTER-CHECKLIST.md` §5.2 and `.claude/skills/incident-triage/SKILL.md`, then harden the Predictor service."
2. **Audit → plan → gate.** Agent states a plan; you approve before it edits (Golden Rule 2).
3. **Build to the contract, not vibes.** The frozen schema in `docs/contracts/` is law; the agent implements to it.
4. **Verify against the rubric bar**, not "it runs." Each section below has the *Excellent* bar quoted — that's the definition of done.
5. **Log prompt changes immediately** (§6). A prompt edited without a logged result is a lost 25%-grade data point.
6. **Never let the session commit/push/deploy** — Cursor doesn't honor your Claude-Code deny-floor.

Skills available to the agent (canonical root `.claude/skills/`): `incident-triage`,
`rag-evaluation`, `guardrails-testing`, `prompt-engineering-log`, `ec2-deploy`,
`mcp-integration`, `frontend-design`, `peter-evaluation`, `graphify`.

---

## 1. Rubric = your priority map (100%)

Build in ROI order. **Prompt Log (25%) + EC2 Services (25%) = half your grade.**

| # | Criterion | Weight | *Excellent* bar (the target) | PETER PAN status |
|---|---|---|---|---|
| 1 | **Prompt Engineering Log** | 25% | 5 surfaces, 5 iterations each, clear failure analysis, measurable improvement | `[ ]` |
| 2 | **EC2 Services** | 25% | All 4 deployed, Dockerized, correct schema, error handling | `[ ]` |
| 3 | **n8n Flow** | 20% | All nodes, guardrails integrated, router working, parallel EC2 calls | `[ ]` |
| 4 | **Image Analyser** (Predictor) | 10% | Trained, **>75% test accuracy**, handles uncertain inputs gracefully | `[ ]` |
| 5 | **Guardrails** | 10% | Both rails working, well-designed configs, **<5% false-positive rate** | `[ ]` |
| 6 | **WebUI + Ollama** | 10% | Both tabs functional, tuned Ollama prompt, form→n8n, report displayed | `[ ]` |

Two hard numbers the rubric names: **Predictor >75% accuracy**, **Guardrails <5% FP rate**. Track them.

---

## 2. Requirement crosswalk (guideline → PETER PAN)

| Guideline (real estate) | PETER PAN (incident ops) |
|---|---|
| Validate genuine listing (not spam) | Validate genuine ops event (not noise/injection/off-topic) |
| Extract property type, condition, features | Extract service, environment, severity signals, symptoms |
| Classify image → room type + condition 1–5 | Classify metric window → category + severity 1–5 |
| Retrieve similar past listings from KB | Retrieve similar past incidents + runbooks from KB |
| Route residential vs commercial | Route Infra / DB / Application |
| Produce publishable listing brief | Produce actionable TriageReport |

---

## 3. The four layers

| Layer | Guideline | PETER PAN | Status |
|---|---|---|---|
| 1 · UI | Gradio/Streamlit: Ollama assistant + form | Streamlit: SRE assistant tab + incident form | `[ ]` |
| 2 · n8n | 8-node webhook→guardrails→extract→agent→EC2→chain→route | Identical 8-node spine (`n8n/peter-flow.json`) | `[ ]` |
| 3 · EC2 | 4 Dockerized FastAPI services | RAG · Predictor · Guardrails · LangGraph (+ Ingestion/Tools support) | `[ ]` |
| 4 · LLM | Gemini/GPT-4o · Ollama Llama 3 · Llama.cpp | Same 3 tiers; Bedrock Claude declared alt | `[ ]` |

---

## 4. The 8 n8n nodes (20%)

| # | Node | Guideline | PETER PAN | Prompt surface? | Status |
|---|---|---|---|---|---|
| 1 | Webhook | form POST (desc + image URLs) | POST (description + metricWindowRef + reporter) | — | `[ ]` |
| 2 | Guardrails-In | HTTP → EC2, pass/fail | HTTP → `/check/input` | — | `[ ]` |
| 3 | IF | pass/fail branch | same; reject → 200 to machine sources | — | `[ ]` |
| 4 | Info Extractor | Gemini, property fields | Gemini, incident fields, **never infer severity** | **#1** | `[ ]` |
| 5 | AI Agent | GPT-4o, 3 tool calls | GPT-4o, 3 EC2 tools (RAG/Predictor/LangGraph) | **#2** | `[ ]` |
| 6 | LLM Chain | listing brief + parser | TriageReport + pinned JSON schema | **#3** | `[ ]` |
| 7 | Guardrails-Out | no false claims → review | no invented owners/destructive cmds → review | (#4) | `[ ]` |
| 8 | Router | property_type → res/comm | category + P-level → Infra/DB/App + fallback | — | `[ ]` |

Requirement: parallel EC2 dispatch (rubric names "parallel EC2 calls wired correctly"). Verify the agent fans out, not serial.

---

## 5. The four services (25%) — exact contracts + deviation flags

> **Verify your schemas.** The guideline uses specific field names; yours differ (domain
> swap). That's fine — but your `docs/contracts/` must be internally consistent and you
> must be able to name which rubric line each maps to. Deviations are flagged ⚠️.

### 5.1 RAG — `POST /query`
| | Guideline | PETER PAN |
|---|---|---|
| Output | `{similar_listings, insight}` | ⚠️ `{similar_incidents, runbook_refs, insight}` |
| Stack | LangChain · Llama.cpp · ChromaDB · HF embeddings | same |
| Seed | ≥20 synthetic listings | ≥25 runbooks + ≥30 incidents |
| Rule | cite source, no fabrication | citation-enforced, "not in KB" over invention |

Checklist: `[ ]` ≥20-doc corpus seeded · `[ ]` top-3 retrieval · `[ ]` citation validation · `[ ]` no-context refusal · `[ ]` deterministic retrieval floor.

### 5.2 Image Analyser → **Incident Predictor** — `POST /analyse`
| | Guideline | PETER PAN |
|---|---|---|
| Output | `{room_type, condition_score, confidence}` | ⚠️ `{incident_class, severity, confidence}` |
| Model | ResNet-50 / EfficientNet-B0, transfer learning | ⚠️ 1D-CNN/GRU or PatchTST (same transfer-learning method) |
| Data | ≥200 labelled images | ≥400 labelled metric windows (synthetic) |
| Threshold | confidence → "uncertain" | confidence → **EWMA/z-score deterministic floor** |

⚠️ **Biggest deviation.** Rubric bar is **>75% accuracy + graceful uncertain-handling** — that's domain-neutral, so you meet it with the classifier. Keep the **dashboard-screenshot vision fallback** ready in case a grader insists on a literal image model.
Checklist: `[ ]` ≥400 windows · `[ ]` dual head (incident class+severity) · `[ ]` >75% test acc · `[ ]` per-class P/R · `[ ]` augmentation (noise/shift/scale) · `[ ]` uncertainty floor · `[ ]` `.pth` checkpoint + `train.py`.

### 5.3 Guardrails — `POST /check/input` + `POST /check/output`
| | Guideline | PETER PAN |
|---|---|---|
| Output | `{pass, reason, safe_text}` | Frozen `{passed, flags, reason}`; non-empty flags route to human review |
| Stack | NeMo Guardrails · FastAPI · YAML/Colang | same + deterministic regex floor |
| Input rail | genuine listing, right language | genuine ops event, injection block, HE/EN |
| Output rail | no false legal/price/cert claims | no invented owners/versions/paths, no destructive verbs |

`safe_text` is intentionally omitted: blocked incidents are routed to **human review**, not auto-sanitized. `passed` avoids Python's reserved `pass` keyword and is frozen in `GuardrailResult`.
Checklist: `[ ]` dual endpoint · `[ ]` NeMo+Colang · `[ ]` regex floor (kills always-pass/fail) · `[ ]` <5% FP · `[ ]` flagged output → human review.

### 5.4 LangGraph Agent — `POST /agent/run`
| | Guideline | PETER PAN |
|---|---|---|
| Output | `{answer, tools_used, reasoning_steps}` | same (identical contract) |
| Graph | planner → tool exec (RAG+Image) → synthesiser | planner → specialists (RAG+Predictor) → synthesiser |

Checklist: `[ ]` typed StateGraph · `[ ]` deterministic routing · `[ ]` bounded tool calls · `[ ]` partial-failure handling · `[ ]` path tests.

Global services checklist: `[ ]` each has Dockerfile + requirements.txt · `[ ]` `/healthz` · `[ ]` typed schemas · `[ ]` error handling · `[ ]` deployed on EC2.

---

## 6. Prompt Engineering Log (25%) — the biggest single line

Required per-surface format: **V1 baseline → V2/V3 targeted fixes → V4/V5 refinement → Final** with justification and **pass rate on ≥10 test cases**. Failure analysis between versions is what's graded.

| # | Surface | Where | Frozen ≥10-case set | Status |
|---|---|---|---|---|
| 1 | Info Extractor | n8n Node 4 | 10 alerts: missing fields, mixed HE/EN, 1 injection | `[ ]` |
| 2 | AI Agent + tool descriptions | n8n Node 5 | 10 incidents needing different tool combos | `[ ]` |
| 3 | RAG retrieval / citation | RAG service | 10 queries, 3 with no KB match | `[ ]` |
| 4 | Guardrails rails | Guardrails service | 10+10 in valid/invalid, 10+10 out clean/poisoned | `[ ]` |
| 5 | Ollama system prompt | WebUI | 10 chats: off-topic, SLA-bait, injection | `[ ]` |

Rules: freeze the set before V1 · show real regressions · ≥10 cases each · persist run outputs to `/evaluation/` · hash n8n-embedded prompts to detect drift. Deliverable: `docs/prompt-log/` (PDF/DOCX). Skill: `prompt-engineering-log`.

---

## 7. Deliverables checklist (§7)

**Code:**
- `[ ]` n8n flow exported as importable JSON (`n8n/peter-flow.json`)
- `[ ]` 4 service dirs, each with Dockerfile + requirements.txt
- `[ ]` WebUI source + README to run locally
- `[ ]` ChromaDB pre-pop script (≥20 docs — you do ≥55)
- `[ ]` `.pth` checkpoint **or** training script + repro instructions

**Docs:**
- `[ ]` Prompt Engineering Log (PDF/DOCX)
- `[ ]` Own architecture diagram (annotated, not a copy of Figure 1)
- `[ ]` Deployment notes: instance types, ports, **declared deviations**

**Demo (§8):**
- `[ ]` 5–8 min video — the 4 required scenes below

**Submission packaging:**
- `[ ]` Single ZIP `PETERPAN_FinalProject.zip` containing `/code`, `/docs`, `/demo`, top-level `README.md`

---

## 8. Demo video — the 4 required scenes (5–8 min)

The guideline mandates exactly these four. Script them:
1. `[ ]` **Successful end-to-end submission** — incident in → validated TriageReport out.
2. `[ ]` **Input-guardrail failure** — off-topic/injection rejected at `/check/input`.
3. `[ ]` **Output-guardrail failure** — a report with an invented owner/destructive step flagged → human review.
4. `[ ]` **Ollama assistant exchange** — SRE assistant answers on-topic, refuses off-topic/SLA-bait.

Narrate scenes 2–3 like an SRE incident (detection → log trail → human handoff) — that's your brand showing up live.

---

## 9. Deployment + security checklist (§11 + Security Note)

- `[ ]` EC2 t3.large (t3.medium min); Docker; 4 services via compose
- `[ ]` **Security group NEVER `0.0.0.0/0`** — inbound restricted to n8n IP + dev IP only
- `[ ]` Containers non-root; GGUF on EBS
- `[ ]` **No API keys / AWS creds committed** — `.env` + Secrets Manager
- `[ ]` n8n HTTP node URLs point at EC2 private IP (n8n on-instance)
- `[ ]` CloudFormation stack validated (lint) — deploy is a separate gated step
- `[ ]` Deployment notes record instance type, ports, deviations

Local dev order (guideline §11.2): Ollama pull → build/test each service in Docker → seed ChromaDB → curl/Postman each endpoint → build n8n flow on localhost → wire WebUI. You're past most of this.

---

## 10. Optional extensions (extra credit) — PETER PAN native coverage

| Extension | Covered by | Status |
|---|---|---|
| Feedback loop / active learning | guardrail flag → review queue → postmortem → re-ingest → retrain | `[ ]` |
| Multilingual guardrail | HE/EN detection in input rail | `[ ]` |
| Managed vector store | ChromaDB → pgvector, precision@3 benchmark | `[ ]` |
| Monitoring dashboard | observability tab: MTTD/MTTR, guardrail hit-rate, avg severity, last-10 | `[ ]` |

Do **one** well if T1 is done — don't chase all four two weeks out.

---

## 11. Declared deviations (state to Alex upfront)

1. **Domain** — AIOps/incident response instead of real estate. Same capabilities.
2. **Classifier input** — time-series metric windows instead of images (same transfer-learning method; vision fallback ready).
3. **Model additions** — Bedrock Claude alongside Gemini/GPT-4o; pgvector alongside ChromaDB (one-node swaps).
4. **Service count** — 4 graded services + Ingestion/Tools API as supporting infrastructure (ADR 0003). Grader sees four primary; support seams are declared.

---

## 12. Two-week build order (T1 = rubric/demo-critical)

Front-load T1 across all layers regardless of epic order. T3 → Path-to-Production, not this deployment.

**Week 1 — make the graded core solid (T1):**
- `[ ]` n8n happy path + both guardrail-fail branches working end-to-end
- `[ ]` 4 services typed + `/healthz` + fail-safe paths
- `[ ]` Predictor trained >75%, dual head, uncertainty floor, `.pth` saved
- `[ ]` Guardrails dual endpoint + regex floor, FP <5%
- `[ ]` RAG ≥55-doc corpus, citation + no-context refusal
- `[ ]` LangGraph real StateGraph, bounded tools, partial-failure handling
- `[ ]` Start the Prompt Log (all 5 surfaces, V1 baselines + frozen sets)

**Week 2 — log, UI, demo, package (T1 + T2):**
- `[ ]` Prompt Log to V5 on all 5 surfaces with pass rates (25%!)
- `[ ]` Streamlit both tabs + TriageReport render + Ollama assistant tuned
- `[ ]` E2E golden-signal runner green
- `[ ]` Own annotated architecture diagram + deployment notes
- `[ ]` One optional extension (observability tab is cheapest signal)
- `[ ]` Record 4-scene demo · `[ ]` ZIP package · `[ ]` pre-public checklist closed

**T2 (if time):** CloudFormation validate, structured logging + `/readyz`, native ADRs, adversarial-eval expansion.
**T3 (defer → Path-to-Production):** managed pgvector, live Supabase, circuit breakers everywhere, Terraform, Playwright beyond one smoke, React UI.

---

## 13. Pre-submission final gate

- `[ ]` All 6 rubric lines meet the *Excellent* bar (§1)
- `[ ]` Predictor >75% and Guardrails <5% FP — numbers recorded
- `[ ]` 5 prompt surfaces × 5 iterations × ≥10 cases, failure analysis present
- `[ ]` 4 services return correct schema, Dockerized, on EC2
- `[ ]` Demo covers all 4 required scenes
- `[ ]` `docs/PRE-PUBLIC-CHECKLIST.md` closed (secrets/Kaggle/history)
- `[ ]` ZIP built: `/code` `/docs` `/demo` `README.md`
- `[ ]` Deviations documented; architecture diagram is your own
