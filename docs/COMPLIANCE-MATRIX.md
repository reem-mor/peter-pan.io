# PETER PAN — Layer 3 Spec-Compliance Matrix

**Session:** A.6 · **Date:** 2026-07-13 · **Evidence window:** this session only  
**EC2:** `i-00179f890ae161552` / `18.234.123.139` · **Crosswalk:** [`docs/PETER-PAN-SPEC-CROSSWALK.md`](PETER-PAN-SPEC-CROSSWALK.md)

Status legend: **PASS** · **PASS-with-deviation** (declared in register or newly noted) · **GAP** · **GAP-scheduled** (Session D)

Every evidence cell is from a command run on 2026-07-13. Prior docs are not cited as proof.

---

## §4.1 — RAG Service (`:8003`)

| Requirement | Where implemented | Evidence (this session) | Status |
|---|---|---|---|
| `POST /query` accepts alert text and returns similar-incidents + insight (crosswalk) | [`services/rag/rag_service/app.py`](../services/rag/rag_service/app.py) — request `{query, limit}` → `{answer, citations, refused}` | Local: `pytest services/rag/tests/test_rag.py …` → **35 passed**. EC2 curl: `{"answer":"# Orders API Error Spike Runbook…","citations":[{"source_id":"orders_api_error_spike",…}],"refused":false}` | **PASS-with-deviation** — field names differ from `{description}` / `{similar_incidents, insight}`; n8n already uses `{query, limit}`. Map: `citations`≈similar incidents, `answer`≈insight. Add register line #6. |
| Sentence-transformer embedding; same model ingest+query; metadata; mismatch refusal | [`vector_rag.py`](../services/rag/rag_service/vector_rag.py) `EMBED_MODEL_NAME=all-MiniLM-L6-v2`; [`populate_vector_store.py`](../scripts/populate_vector_store.py) imports it | Local unit tests green. Local populate: `count 24 -> 24`. **Post-fix EC2:** collection meta `embedding_model: all-MiniLM-L6-v2`, count 24. | **PASS** |
| ChromaDB top-3 with distances; weak retrieval → honest refusal | `MAX_DISTANCE=0.8` in `vector_rag.py`; refusal in `/query` | **Post-fix EC2:** `PETER_VECTOR_BACKEND=chroma`; `chromadb`/`sentence_transformers` import OK; live query returns `(per INC-101…)` excerpts; off-topic → `refused:true`. | **PASS** |
| Pre-population: idempotent, ≥20 incidents, 6 classes ≥3 each | [`scripts/populate_vector_store.py`](../scripts/populate_vector_store.py) + [`incidents_seed.json`](../services/rag/data/incidents_seed.json) | Local + **EC2 twice:** `count 24 -> 24`, per-class 4 each. | **PASS** |
| Citations in insight; fabrication fails closed | Generator prompt [`surface-3-rag.systemprompt.txt`](prompt-log/prompts/surface-3-rag.systemprompt.txt); `/query` citations | **Session D EC2:** live `/query` with Chroma+GGUF returns synthesized insight citing `(per INC-101…)` in answer and citations; off-topic still refuses. | **PASS** |
| llama.cpp GGUF generation on EC2 | [`generator.py`](../services/rag/rag_service/generator.py) behind `GGUF_MODEL_PATH`; [`scripts/enable_gguf_ec2.sh`](../scripts/enable_gguf_ec2.sh) | **Session D EC2 (2026-07-14):** `/home/ubuntu/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf` (4.1G); `GGUF_MODEL_PATH=/models/…` in `.env`; `llama_cpp 0.3.8` in container; disk `29G 19G used 9.1G free`; RAM `7.6Gi` (~5.1Gi avail). First authenticated `/query` ~6.3 min (CPU 7B load+gen on t3.large). | **PASS** |

---

## §4.2 — Predictor (`:8002`) *(crosswalk of Image Analyser)*

| Requirement | Where implemented | Evidence (this session) | Status |
|---|---|---|---|
| Seeded `train.py`; ≥200 samples; 70/15/15; per-class in metrics | [`services/predictor/train.py`](../services/predictor/train.py); [`artifacts/metrics.json`](../services/predictor/predictor_service/artifacts/metrics.json) | `metrics.json`: `samples_per_class=50` (300 total), `split: 70/15/15 stratified by seed`, `seed: 42`, per-class P/R present. `predictor.pth` present (49321 bytes). | **PASS** |
| Transfer-learning structure; `.pth` at startup; CPU inference | `train.py` (1D-CNN pretrain + frozen head); [`torch_classifier.py`](../services/predictor/predictor_service/torch_classifier.py) | EC2: `torch 2.13.0+cpu`, `cuda False`. Local: `pytest services/predictor/tests --no-cov` → **54 passed**. | **PASS-with-deviation** — in-domain 1D-CNN transfer (not ImageNet ResNet); matches declared modality swap (register #2). Endpoint is `POST /analyse` not `/predict` — note as register #7. |
| `metrics.json`: accuracy, per-class P/R, confusion, threshold + justification | same artifact | `test_accuracy=0.881` (>75%); threshold `0.5` with val grid; notes: *"Synthetic shape-separable windows make this task easy by construction…"*. | **PASS** (honest >75% on easy synthetic task). |
| Below-threshold → uncertain fallback; EWMA floor; redis cross-domain | `app.py` tiers + `match_context` | Local: `test_analyse_below_threshold_surfaces_uncertain_fallback` in suite. EC2 curl redis markers → `{"incident_class":"memory_leak",…,"classifier":{"engine":"context"}}` with EWMA `method":"ewma-floor"`. | **PASS** |

### §4.2 — Image Analyzer (`:8007`) — status only (Alex ruling)

| Spec letter item | Status |
|---|---|
| Exists as FastAPI service + Dockerfile | **Yes** — healthz 200 on EC2; 2 local tests passed |
| ResNet/EfficientNet backbone + trained heads | **No** — [`ImageAnalyzerModel`](../services/image-analyzer/image_analyzer_service/models.py) is Stage A fixture (PIL dims → room type) |
| Dataset / threshold / `.pth` | **Absent** |
| Invoked by n8n | **No** — Predictor is the graded crosswalk path |
| Ruling needed | **Alex:** grade Predictor crosswalk vs also require vision Image Analyzer |

---

## §4.3 — Guardrails (`:8004`)

| Requirement | Where implemented | Evidence (this session) | Status |
|---|---|---|---|
| Dual endpoints `/check/input` + `/check/output` | [`guardrails_service/app.py`](../services/guardrails/guardrails_service/app.py) | EC2: valid input → `{"passed":true,"flags":[],…}`; destructive → `passed:false` with `destructive_data_action`; output endpoint returned JSON with `passed/flags/reason`. | **PASS** |
| Input rail: junk/off-topic/injection rejected; valid pass; FP <5% | [`rules.py`](../services/guardrails/guardrails_service/rules.py) regex floor + `scan_off_topic`; [`test_floor_priority.py`](../services/guardrails/tests/test_floor_priority.py) | Valid alert PASS. Destructive REJECT. **Post-fix off-topic pasta:** `passed:false, flags:[off_topic]`. FP suite green; full guardrails suite **78 passed**. | **PASS** |
| Output rail: fabricated / invented RCA / uncited blocked; flag-for-review | `test_check_output.py`; E2E flagged | Local: `test_uncited_claim_fails`, destructive_step, invented_owner in suite. E2E: `pytest evaluation/tests/test_run_e2e.py -k flagged --no-cov` → **2 passed**. Live EC2 invented citation with non-empty quote **passed** (floor checks empty quotes / destructive steps / owner via Tools — not full LLM fabrication auditor). | **PASS** for deterministic floors + E2E review-queue path; **GAP** for prompt-based fabricated-metric auditor. |
| Schema `{passed, flags, reason}` vs `{pass, reason, safe_text}` | `GuardrailResult` in contracts | Live JSON uses `passed`/`flags`/`reason`. Register #3. | **PASS-with-deviation** (#3) |
| Rails are versioned prompts wired to prompt-log | Prompt files + suites under `docs/prompt-log/` | Created this session: `surface-4-topic-detection.txt`, `surface-4-output-auditor.txt`, `test-suites/surface-4-guardrails.cases.json`. **Not wired** into live service (NoopPolicyEngine + regex). | **GAP** — scaffolding exists; live wiring pending. |
| Deterministic floor overrides engine "pass" | `test_floor_priority.py` + `NoopPolicyEngine` | `test_regex_floor_overrides_policy_engine_pass_on_input/output` passed this session. | **PASS** |

---

## §4.4 — LangGraph Agent (`:8006`)

| Requirement | Where implemented | Evidence (this session) | Status |
|---|---|---|---|
| `POST /agent/run` returns `{answer, tools_used, reasoning_steps}` | [`langgraph_agent/app.py`](../services/langgraph-agent/langgraph_agent/app.py) returns validated **TriageReport** | EC2 curl → keys: `incident_id, category, p_level, summary, probable_cause, citations, owner_team, …` — not the three-field course shape. | **PASS-with-deviation** — richer incident brief; add register #8. |
| Three-node graph: planner → tools → synthesiser | [`graph.py`](../services/langgraph-agent/langgraph_agent/graph.py) `plan` → `specialists` → `synthesise` | `test_graph_visits_plan_then_specialists_then_synthesise` green in `pytest services/langgraph-agent/tests/test_graph.py` (coverage 98%). | **PASS** |
| Tools invoke RAG + Predictor (crosswalk) | Graph calls RAG + Tools API; Predictor is n8n Node 5 | Live redis cross-domain: citations include `tool:service_context`, `tool:similar_incidents`; summary mentions RAG guidance. Predictor **not** called inside LangGraph (by design — commander calls Predictor first). | **PASS-with-deviation** — Predictor via n8n; LangGraph = RAG + Tools specialists. Register #9. |
| Multi-step SLO/signals question coherent | Live `question` on redis incident | Summary includes symptom + question; probable_cause from similar incidents ("Cache eviction storm"); owner Infra SRE. RAG returned insufficient data (TF-IDF/backend gap) but Tools path filled citations. | **PASS** (degraded RAG) |
| 10-benchmark-query set for tool-description iterations | [`evaluation/langgraph_benchmark_queries.json`](../evaluation/langgraph_benchmark_queries.json) | **Created this session** — 10 frozen queries (iterations = Prompt Log work). Prior `tool_evaluation_cases.json` is 4 Tools-API route cases, not this set. | **PASS** (queries frozen now) |

---

## §4 cross-cutting

| Requirement | Where implemented | Evidence (this session) | Status |
|---|---|---|---|
| Every service: FastAPI + Dockerfile + own `requirements.txt` | `services/*` | Inventory: all **10** dirs have both (`dashboard-generator`, `fixture-llm`, `guardrails`, `image-analyzer`, `ingestion`, `integration-stubs`, `langgraph-agent`, `predictor`, `rag`, `tools-api`). | **PASS** |
| Deployed on EC2; ports exposed; SG restricted | [`docker-compose.ec2.yml`](../docker-compose.ec2.yml); SG `sg-01c3120dcf290c20c` | `test_ec2_public_health.py` → **all 10 + Grafana healthy**. `aws ec2 describe-security-groups`: every inbound rule `62.56.234.234/32`; **no `0.0.0.0/0`**. Ports: 22, 3000, 5678, 8001–8008, 8020. | **PASS** |
| Dashboard Generator: validator green; POST creates dashboard; Playwright panels | [`services/dashboard-generator/`](../services/dashboard-generator/) | Local pytest green. **Post-fix:** `GRAFANA_API_TOKEN` set; POST creates real dashboard; Grafana search finds `pp-orders-api-errors` (3 panels). Playwright screenshot shows panels **5xx error rate / Request rate / Error budget burn** rendered (values "No data" without scrape targets — layout proof). | **PASS** |
| `/healthz` suite 10/10 + Grafana | scripts | Public: 10/10 + Grafana. Local `--include-support`: 10/10. `docker compose config --quiet` silent. | **PASS** |

---

## §8 — Technology Summary (Layer-3 rows)

| Spec row | Check (this session on EC2) | Status |
|---|---|---|
| RAG: LangChain + Llama.cpp + ChromaDB on EC2 | **Session D:** `chromadb OK`, `sentence_transformers OK`, `llama_cpp 0.3.8 OK`; Chroma count 24; GGUF 4.1G on EBS mounted at `/models`. `langchain` absent → custom prompt (register #10). | **PASS-with-deviation** (#10) for LangChain; Chroma + GGUF **PASS** |
| Image Analyser: PyTorch + ResNet/EfficientNet | Predictor: PyTorch CPU **OK** (crosswalk). Image-analyzer: fixture only, no ResNet. | **PASS-with-deviation** (#2) for Predictor; Image Analyzer **status-only / Alex** |
| Guardrails: NeMo Guardrails + FastAPI | FastAPI OK; custom regex floor (+ off-topic) + `NoopPolicyEngine`; NeMo not installed | **PASS-with-deviation** (#11) |
| LangGraph Agent: LangGraph + FastAPI | `pip show langgraph` → **Version: 0.4.8** (pinned in requirements) | **PASS** |
| Vector Store: ChromaDB on EC2 (local) | Volume `rag-chroma` at `/data/chroma`; count 24; not external SaaS | **PASS** |
| Model Files: GGUF on EC2 (EBS) | `/home/ubuntu/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf` (4.1G); `GGUF_MODEL_PATH=/models/…`; 9.1G disk free | **PASS** |

---

## §7 — Deliverables inventory (Layer-3 items, status-only)

| # | Deliverable | Status | Owner / note |
|---|---|---|---|
| 1 | Each EC2 service in own dir with Dockerfile + requirements.txt | **Exists** | Cross-ref §4 table (10/10) |
| 2 | Pre-population script committed, ≥20 incidents | **Exists** — 24×6×4; **applied on EC2** (count 24→24) | RAG |
| 3 | PyTorch checkpoint committed or reproducible | **Exists** — `predictor.pth` + `metrics.json` committed; `train.py` reproduce path present (not re-trained this session) | Predictor |
| 4 | Deployment notes: instance type, ports, deviations | **Partial** — ARCHITECTURE + crosswalk register cover most of §7.2; dedicated "deployment notes" doc not separate | Doc gap only (do not write in this session per plan) |
| 5a | n8n flow export (Layer 2) | **Exists** — `n8n/peter-flow.json` | Layer 2 |
| 5b | WebUI + README (Layer 1) | Skeleton / pending polish | Layer 1 |
| 5c | Architecture diagram (own version) | **Not started** | Author |
| 5d | Prompt Log PDF/DOCX export | **Missing** | Author (25%) |
| 5e | ZIP `/code` `/docs` `/demo` | **Missing** | Submission packaging |

---

## §6 — Prompt Log scoreboard (5 surfaces)

| Surface | Prompt file(s) | Frozen suite (≥10) | Versions done | Format vs §6.1 | Status |
|---|---|---|---|---|---|
| 1 Extractor (L2) | `surface-1-extractor.systemprompt.txt` | Yes (12 cases) | **V1 only** (6/12); V2–Final planned | Matches skill structure | In author hands |
| 2 Agent (L2) | systemmessage + tools.json | Yes (12 cases) | V1 text recorded; **live baseline BLOCKED → Layer 4** | Matches | Blocked on live provider |
| 3 RAG (L3) | `surface-3-rag.systemprompt.txt` (wired to generator; byte-match tested) | **Yes — created this session** (12 cases) | **0** of V1–V5 | N/A until first entry | **Author iterations remain** |
| 4 Guardrails (L3) | topic + output auditor **scaffolds created**; not wired to service | **Yes — created this session** (13 cases) | **0** of V1–V5 | N/A | **Author iterations + wiring remain** |
| 5 Ollama UI (L1) | — | — | 0 | — | Layer 1 session |

**Format drift flag:** Surfaces 1–2 follow V1 → V2–V5 → Final structure correctly. Surface 1 notes harness approximation honestly. No format drift found; do not invent V2–V5 without real runs.

---

## Caveman summary (lecturer)

Something breaks in production. Our Layer-3 services classify what kind of break it is, look up what happened last time (Chroma + Mistral GGUF on EBS), block unsafe text, and deep-reason with a three-step agent — all on one locked-down EC2 box. Remaining graded work is mostly Prompt Log iterations, not a service rewrite.

---

## Action footer

### Session D — GGUF on EBS (completed 2026-07-14)
- **D1:** `llama-cpp-python==0.3.8` in [`services/rag/requirements.txt`](../services/rag/requirements.txt); RAG Dockerfile build deps (`cmake`, `git`, `build-essential`, `libgomp1`)
- **D2:** [`docker-compose.ec2.yml`](../docker-compose.ec2.yml) mounts `/home/ubuntu/models` → `/models:ro`
- **D3:** [`scripts/enable_gguf_ec2.sh`](../scripts/enable_gguf_ec2.sh) — idempotent download + env patch + rebuild
- **D4:** EC2 evidence: model on EBS, `llama_cpp 0.3.8`, live `/query` returns GGUF-synthesized insight with `(per INC-101…)` citations (~6 min first request on t3.large CPU)

### Gaps fixed this session (Phase 6 — approved “all”)
- **G1:** `chromadb` + `sentence-transformers` (+ torch CPU) in [`services/rag/requirements.txt`](../services/rag/requirements.txt); RAG image rebuilt on EC2
- **G2:** `PETER_VECTOR_BACKEND=chroma`; populate idempotent `24→24` on instance volume
- **G3:** Grafana service-account token + Prometheus datasource UID; real dashboard POST; Playwright panels render
- **G4:** Deterministic `off_topic` floor in [`rules.py`](../services/guardrails/guardrails_service/rules.py); pasta recipe rejected; FP suite still green
- **G5:** Deviations **#6–#11** written into [`docs/PETER-PAN-SPEC-CROSSWALK.md`](PETER-PAN-SPEC-CROSSWALK.md)
- Also: frozen LangGraph 10-query set + Prompt Log surface 3/4 suites (earlier in session)

### Needs Alex's ruling
- Grade **Predictor crosswalk** alone vs require a real **Image Analyzer** (ResNet/EfficientNet) for §4.2.

### What remains of the 25% Prompt Log (in your hands)
| Surface | Remaining |
|---|---|
| 1 | V2–V5 + Final (suite exists) |
| 2 | Live V1–V5 once Layer-4 provider bound |
| 3 | Write `surface-3-rag.md` V1–V5 + Final against frozen suite |
| 4 | Iterate V1–V5 + Final (scaffolds + suite exist; regex floor is live — document that honesty) |
| 5 | Entire surface (Layer 1) |
| Export | PDF/DOCX for submission |

---

## Newly recommended deviations register lines

Written into the crosswalk register as **#6–#11** (Phase 6 / G5).
