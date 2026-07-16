# Product story — from PITER to PETER PAN

**Audience:** lecturer, employers, portfolio reviewers, future enterprise buyers.  
**Domain:** AIOps / incident operations — **not** real estate. The course guideline’s
property-triage scenario is only a **capability map** (same graded surfaces, different vertical).

---

## 1. One-line product

> **PETER PAN** is a self-hostable, guarded, agentic incident-triage platform:
> alert in → enrich from history → classify → safety-check → route → structured
> `TriageReport` (and optionally a purpose-built Grafana dashboard).

---

## 2. Origin story — what PITER was

**PITER** was the mid-course project: connect **Knowledge → RAG**.

| Idea | Meaning in the mid-term |
|:---|:---|
| Knowledge | Runbooks, past incidents, ownership docs as a corpus |
| RAG | Embed → retrieve → generate **with citations** |
| Outcome | An operator can ask “what happened last time?” and get grounded answers |

PITER proved the retrieval + grounding loop. It did **not** yet own the full
intake → classify → guard → route → brief pipeline that production NOC work needs.

---

## 3. Evolution — why PETER PAN

**PETER PAN** is the final-project product: connect **Observability → Monitoring**.

| Acronym / word | Meaning |
|:---|:---|
| **PETER** | **P**riority · **E**nrichment · **T**riage · **E**scalation · **R**esolution |
| **PAN** | The **panoramic** view of the incident — context, class, citations, route, and a visual |

The course asked for a four-layer production-style AI system (UI → n8n → FastAPI
microservices → LLM tier). The guideline’s real-estate listing pipeline maps
**1:1** onto incident ops:

| Course capability (guideline) | PETER PAN capability |
|:---|:---|
| Listing intake form | Signal / alert intake (WebUI + Ingestion) |
| Input / output safety rails | Guardrails `{passed, flags, reason}` + regex floor |
| Structured field extraction | n8n Information Extractor (ops fields) |
| Image CNN (6 classes) | **Predictor** — PyTorch over metric windows (6 `incident_class`) |
| RAG over past listings | RAG over incidents + runbooks (cite or refuse) |
| LangGraph multi-step agent | LangGraph triage specialists (RAG + Tools) |
| Residential / commercial router | 6→3 routing category in n8n Router only |
| Listing brief | Frozen `TriageReport` |
| Ollama assistant | Streamlit SRE assistant (fixture-first demo path) |
| Extension: monitoring dashboard | Grafana **Dashboard Generator** (draw the problem) |

**Design principle that survives the classroom:** *models propose; deterministic
code and frozen contracts decide.* Severity, routing category, and hard safety
rules are never “whatever the LLM said.”

---

## 4. Four layers (product shape)

HTTP between layers. n8n is the conductor — it does not own business logic.

| Layer | Role | Repo home |
|:---|:---|:---|
| **L1 · Experience** | Operator console + optional local LLM chat | [`ui/`](../ui/) |
| **L2 · Orchestration** | 8-node PETER flow (webhook → rails → extract → agent → brief → route) | [`n8n/`](../n8n/) |
| **L3 · Platform services** | Graded FastAPI units + ingress / tools / dashboard seams | [`services/`](../services/) |
| **L4 · Model tier** | Task-routed `LLMClient` — fixture → Bedrock / Gemini / Ollama / Llama.cpp | [`docs/llm_client/`](llm_client/) |

Full topology: [`ARCHITECTURE.md`](ARCHITECTURE.md) · diagrams:
[`peter-pan-system.mmd`](peter-pan-system.mmd), [`peter-pan-n8n-flow.mmd`](peter-pan-n8n-flow.mmd).

---

## 5. Market context — who else plays here

### Commercial incident / AIOps platforms

| Product | Positioning (short) | PETER PAN differentiates by… |
|:---|:---|:---|
| [PagerDuty AIOps](https://www.pagerduty.com/platform/aiops/) | Enterprise alert noise reduction + on-call | Self-hostable stack; frozen contracts; fixture-first offline demo; explicit deterministic floors |
| [Rootly](https://rootly.com/) | Incident lifecycle + AI assist in Slack | Open architecture (n8n + FastAPI); graded RAG/guardrails/PyTorch surfaces you can audit |
| [FireHydrant](https://firehydrant.com/) | Structured IR workflows + timelines | Product-shaped **triage brain** (class → route → `TriageReport`) not only process tooling |
| [incident.io](https://incident.io/) | Modern IR orchestration | Portable compose/EC2 demo; no SaaS lock-in for the core path |

### Open-source / agentic IR neighbours

| Project | Positioning (short) | PETER PAN differentiates by… |
|:---|:---|:---|
| [Aurora (Arvo AI)](https://github.com/Arvo-AI/aurora) | LangGraph agents + multi-cloud investigation | Separates **n8n orchestration** from **service units**; NeMo/regex guardrail floors; course-aligned prompt-log discipline |
| [IRAS](https://github.com/krishnashakula/IRAS) | LangGraph IR with HITL approval | Fixture-first golden path; Tools API + Ingestion seams; CloudFormation single-node demo |
| Multi-RAG / AIOps demos (various LangGraph+RAG repos) | Diagnostic agents over KB | Production-minded contracts, CI E2E, Dashboard Generator headline, locked scope honesty |

PETER PAN is **not** trying to replace PagerDuty’s on-call graph on day one.
It is a **sellable pattern for regulated / self-host environments**: bring your
compose stack, keep secrets local, prove every graded AI surface, and never let
the LLM override safety floors.

---

## 6. What you would sell (enterprise narrative)

**Buyer:** Platform / SRE / AI Engineering lead who needs *trustworthy* AI triage
before agents get write access to production.

**Offer (portfolio → product path):**

1. **Guarded intake** — input rails kill junk and injection before spend.
2. **Grounded enrichment** — RAG that cites or refuses; no invented runbooks.
3. **Deterministic classification** — PyTorch + EWMA floor; 6 classes → 3 routes.
4. **Operator-visible brief** — `TriageReport` schema frozen for n8n + UI + eval.
5. **Panoramic visual** — generated Grafana dashboard for *this* incident.
6. **Demo that never depends on a live API** — fixture-first Stage A path.

**Honest packaging:** Stage A is demo-scale synthetic data on a single EC2 /
local compose node. Multi-region HA, Redis, K8s, and feedback-loop retrain are
**roadmap / out of scope** for the graded build (see locked decisions in
[`CLAUDE.md`](../CLAUDE.md)).

---

## 7. How to tell it in 60 seconds

1. Mid-term **PITER** = Knowledge → RAG (grounded answers).  
2. Final **PETER PAN** = Observability → Monitoring (full triage product).  
3. Course real-estate guideline = **rubric capabilities**, not the product domain.  
4. Four layers: UI → n8n → FastAPI → models.  
5. Differentiator: **deterministic floors + frozen contracts + fixture-first demo**
   plus the panoramic dashboard moment.

---

## Related docs

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — layer contracts and inventory  
- [`PETER-PAN-SPEC-CROSSWALK.md`](PETER-PAN-SPEC-CROSSWALK.md) — guideline deviations register  
- [`PETER-PAN-PROJECT-MASTER-DOC-EN.md`](PETER-PAN-PROJECT-MASTER-DOC-EN.md) — lecturer-facing master narrative  
- [`presentation/DEMO-SCRIPT.md`](presentation/DEMO-SCRIPT.md) — recording script  
