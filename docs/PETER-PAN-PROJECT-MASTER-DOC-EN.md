# PETER PAN — End-to-End Project Document
### AIOps Incident Triage Platform · AI Engineering Final Project
**Re'em Mor · Branch: `feat/stage-a-enterprise-stabilization` · Demo: ~2 weeks**

---

## 1. The Idea in One Sentence (for the lecturer)

> The course gave us a real-estate property triage pipeline. I performed a **one-to-one crosswalk** of that exact architecture — same layers, same services, same prompt surfaces — into the domain I work in every day in production: **incident triage in an SRE/NOC environment**. Every requirement in the course guideline maps to a parallel component in my system.

### The Pitch (2–3 sentences):
PETER PAN connects **Observability to Monitoring**: when an alert comes in, the system automatically enriches it from logs and metrics (RAG), classifies it into one of 6 incident classes (a PyTorch model), runs guardrails on both input and output, and routes it to the right team. The core differentiator: instead of maintaining hundreds of static Grafana dashboards — **the LLM generates a dedicated dashboard for the specific incident in real time** (builds the JSON and posts it to the Grafana API). All of it grounded in real production experience across 500+ nodes.

### The Name:
**PETER PAN** = **P**riority · **E**nrichment · **T**riage · **E**scalation · **R**esolution — and **PAN** is no longer an acronym but a word: **the Panoramic view of your incidents**. (The mid-term project, PITER, connected Knowledge to RAG; PETER PAN connects Observability to Monitoring.)

---

## 2. Crosswalk Table — Course Requirements vs. My Implementation

| # | Course Requirement (Real Estate) | My Implementation (Incidents) | Status |
|---|---|---|---|
| 1 | Listing intake: description + images | Alert intake: payload + logs/metrics context | Done |
| 2 | Guardrails input: spam / off-topic | Guardrails input: invalid alerts / junk / injections | Done |
| 3 | Information Extractor: structured fields from text | Extractor: service, severity, region, error signature | Done |
| 4 | Image Analyser (PyTorch CNN, 6 room types + condition score) | **Predictor (PyTorch, 6 incident classes + confidence)** | Done |
| 5 | RAG: top-3 similar listings from ChromaDB | RAG: similar past incidents + runbooks | Done |
| 6 | LangGraph agent: complex multi-step questions | LangGraph agent: triage reasoning (planner→tools→synth) | Done |
| 7 | Router: residential vs commercial | Router: 3-way routing category (derived from the 6 classes) | Done |
| 8 | Structured listing brief for publication | Structured incident brief + escalation payload | Done |
| 9 | Guardrails output: fabricated claims | Guardrails output: `{passed, flags, reason}` | Done |
| 10 | WebUI + Ollama assistant | Streamlit + Ollama incident assistant | Done |
| 11 | Extension: Monitoring Dashboard | **Dynamic Grafana Dashboard Generator** — the headline | To build |
| 12 | Extension: Feedback Loop | Feedback loop (reviewer queue → retrain) | Roadmap |

---

## 3. The Architecture — Layer by Layer

### Layer 1 — User Interface (Streamlit + Ollama)
**What it does:** Two parts, exactly per the requirement.
1. **Assistant Tab** — chat against a local Ollama server (Llama 3), with a system prompt grounding it as an incident assistant: answers operational questions only, refuses off-topic requests, never invents values.
2. **Alert Submission Tab** — a form for submitting an alert (description, service, severity, context files). Submission = POST to the n8n webhook. What comes back: a complete incident brief + a link to the freshly generated dashboard.

**How to explain it to the lecturer:** "This is the gateway — a user (a NOC engineer) submits an alert or asks a question, exactly like a real-estate agent submitting a listing."

### Layer 2 — n8n Orchestration (8 nodes)
**What it does:** The conductor of the orchestra. A single flow:

| Node | Role | Course Equivalent |
|---|---|---|
| 1. Webhook | Receives the alert from the UI | Webhook Trigger |
| 2. Guardrails Input | POST to the guardrails service — `{passed, flags, reason}` | Node 2 |
| 3. IF Branch | fail → rejection path, pass → continue | Node 3 |
| 4. Information Extractor (Gemini) | Structured fields: service, region, error type... | Node 4 — prompt surface #1 |
| 5. AI Agent | Dispatches tools: RAG, Predictor, LangGraph in parallel | Node 5 — prompt surface #2 |
| 6. LLM Chain | Synthesizes everything into an incident brief (Structured Output Parser) | Node 6 |
| 7. Guardrails Output | Validates the output before returning it | Node 7 |
| 8. Router | 3-way routing by `incident_class` | Node 8 |

**How to explain it to the lecturer:** "n8n does no AI itself — it only decides who talks to whom and in what order. Every node maps 1:1 to a node in the requirements."

### Layer 3 — EC2 Microservices (FastAPI + Docker, t3.large + docker-compose)

| Service | Endpoint | Input → Output | Stack | Course Equivalent |
|---|---|---|---|---|
| **RAG** | POST /query | alert text → similar incidents + insight | LangChain · Llama.cpp (GGUF) · ChromaDB | RAG Service |
| **Predictor** | POST /predict | alert features → `{incident_class, confidence}` (6 classes) | PyTorch, transfer learning | **Image Analyser** |
| **Guardrails** | POST /check/input, /check/output | text → `{passed, flags, reason}` | NeMo Guardrails / rule engine + FastAPI | Guardrails Service |
| **LangGraph** | POST /agent/run | complex question → `{answer, tools_used, reasoning_steps}` | LangGraph (planner→tools→synthesiser) | LangGraph Agent |
| **Ingestion** | internal | Loads synthetic incidents into the vector store (20+ records) | pre-population script | Pre-population script |
| **Dashboard Generator** ⭐ | POST /dashboard | incident context → Grafana JSON → dashboard URL | LLM + Grafana HTTP API | Extension: Monitoring Dashboard |

**An important note on the Predictor:** the requirement specifies a CNN for images. My crosswalk: a classifier over incident features — the exact same idea (transfer learning, 6 classes, confidence threshold with an uncertain label, accuracy reported on a test set). This is the justification to present if the lecturer asks why there are no images: **my domain is logs and metrics; the learning objective — training and serving a PyTorch model as a service — is fully met.** (If the lecturer insists on vision — fallback: classifying screenshots of graphs/dashboards into anomaly categories. Ask him early, not at submission.)

### Layer 4 — LLM Tier (fixture-first)
- **Local Ollama** (Llama 3) — the assistant in the UI.
- **Llama.cpp + GGUF** — local inference in the RAG service.
- **Gemini / Bedrock** — n8n LM nodes (Extractor, Agent).
- **Working principle:** fixture-first — every demo scenario has a deterministic fixture; the live path is a bonus, not a dependency. The demo never fails because an external API is slow.

### ⭐ The Headline: Dynamic Dashboard Generator
**The problem:** real organizations maintain hundreds of static dashboards "just in case," and most are irrelevant to the current incident.
**The solution:** "A customer is experiencing a payments issue" → the LLM builds a dedicated Grafana dashboard JSON (only the relevant panels: latency, error rate, throughput for that service) → POST to the Grafana HTTP API → a link comes back within seconds.
**How to explain it to the lecturer:** "Grafana by default = you build dashboards by hand. I add a layer: the system translates a natural-language problem description into a live dashboard. That's the 'draw me the problem.'"

---

## 4. Prompt Engineering Log — 25% of the Grade (!)

Five surfaces, 5 iterations each, 10+ test cases per surface:

| # | Surface | My Component | What Gets Documented |
|---|---|---|---|
| 1 | Information Extractor | n8n Node 4 | Field extraction with no fabrication, graceful handling of missing fields |
| 2 | AI Agent system prompt | n8n Node 5 | Tool descriptions — does the agent pick the right tool |
| 3 | RAG retrieval prompt | RAG service | Source citation, no fabricated details |
| 4 | Guardrails rails | Guardrails service | Minimizing false positives on valid alerts |
| 5 | Ollama system prompt | Streamlit assistant | Off-topic refusal, resistance to prompt override |

**Format per iteration:** V1 baseline → V2–3 (specific failure in one sentence → fix → result) → V4–5 refinement → Final: the final prompt + justification of every design decision + pass rate.

**(Optional sixth surface for bonus: the Dashboard Generator prompt — valid JSON, relevant panels only.)**

---

## 5. Deliverables — Submission Checklist

- [ ] n8n flow exported as JSON (importable)
- [ ] Source code for 4+ services, each with a Dockerfile + requirements.txt
- [ ] WebUI (app.py) + README for local run
- [ ] ChromaDB pre-population script (20+ synthetic incidents)
- [ ] PyTorch checkpoint (.pth) or training script + reproduction instructions
- [ ] Prompt Engineering Log (PDF/DOCX)
- [ ] **My own** architecture diagram (not a copy of Figure 1) annotating design decisions
- [ ] Deployment notes: instance types, ports, deviations from the spec (including the crosswalk justification)
- [ ] 5–8 minute video: successful E2E · input guardrail fail · output guardrail fail · Ollama conversation
- [ ] ZIP: `TEAMNAME_FinalProject.zip` → /code · /docs · /demo · README.md

## 6. Rubric Mapping

| Criterion | Weight | Where I Stand |
|---|---|---|
| n8n Flow | 20% | Built — verify parallel calls + router |
| EC2 Services | 25% | Built — verify schemas + error handling |
| Predictor (=Image Analyser) | 10% | Built — document accuracy >75% on a test set |
| Guardrails | 10% | Built — measure false-positive rate <5% |
| **Prompt Log** | **25%** | **The biggest gap — start immediately** |
| WebUI + Ollama | 10% | Built — polish |
| Extensions (bonus) | + | Dashboard Generator = official extra credit |

## 7. 12-Day Plan

| Days | Task |
|---|---|
| 1–2 | Merge gate → PR → merge · local Grafana running (`docker run -d -p 3000:3000 grafana/grafana-oss`) |
| 3–6 | Dashboard Generator service + 3–4 fixtures (payments latency, disk pressure, error spike) + live LLM path |
| 5–8 (overlapping) | Prompt Engineering Log — 5 surfaces, real iterations with test cases |
| 9–10 | E2E demo scenario + video recording covering the 4 required segments |
| 11–12 | Buffer: EC2 verification, README, diagram, ZIP |

---

## 8. Cursor Skills — What to Add and Why, by Phase

The principle: a skill = instructions the agent loads only when relevant, instead of a giant prompt every time. Structure: `.cursor/skills/<name>/SKILL.md` (or rules in `.cursor/rules/*.mdc`).

### Infrastructure — always active
| Skill/Rule | Source | Why |
|---|---|---|
| `karpathy-guidelines.mdc` | multica-ai/andrej-karpathy-skills | Already in use — surgical changes, no silent assumptions, goal-driven |
| `peter-pan-locked-decisions` | **write yourself** | The locked decisions: guardrail schema `{passed, flags, reason}` · 6 classes · `incident_class` · fixture-first · CloudFormation · no Twilio/HITL/P5. Saves repeating them in every prompt and prevents the agent from "fixing" things backwards |

### By project phase
| Phase | Skill to Add | What It Contains |
|---|---|---|
| Days 1–2: merge gate | (nothing new — existing rules suffice) | |
| Days 3–6: Dashboard Generator | `grafana-dashboard-json` — **write yourself** | Grafana dashboard JSON schema (panels, targets, datasource uid), validation rules, one working example dashboard, the Grafana HTTP API endpoint + auth. Without this the agent will invent schema fields |
| Days 3–6 | `fastapi-service-conventions` — **write yourself** | Your existing service template: directory structure, contracts.py, pytest conventions, Dockerfile pattern — so the new service looks like the existing ones |
| Days 5–8: Prompt Log | `prompt-log-format` — **write yourself** | The exact log format from the requirements (V1→V5, failure→fix→result, 10 test cases) so the agent produces entries in the right format without re-explaining |
| Days 9–10: demo | `demo-script-guard` — **write yourself** | The list of 4 video scenarios + one rule: any code change at this stage must not break fixtures |

### Rule of thumb, explained simply:
> **Rule** = a law that always applies (style, locked decisions).
> **Skill** = knowledge loaded only when working on a specific topic (Grafana schema, log format).
> Every skill you write = fewer repetitions in prompts and fewer agent mistakes.

---

## 9. The Demo Closing Line

> "PITER handled the knowledge. PETER PAN gives you the pan — the full panoramic picture of your incidents, including a dashboard that didn't exist 30 seconds ago."
