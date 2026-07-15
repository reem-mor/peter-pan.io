# PETER PAN — Spec Crosswalk (Course §3.1 + §4, Incident Domain)

Mirror-structure translation of the course spec. Left column of every mapping
= course original; the text itself = my project. Written so the lecturer can
read this side-by-side with the guideline.

---

## 3.1 Node Descriptions — Incident Triage Pipeline

### Node 1 — Webhook Trigger
Receives the form POST from the Streamlit UI. Parses the incoming JSON body
containing the alert description, service name, severity hint, and context
(log excerpts / metric snapshots). Passes the payload to node 2.
*(Course: property description + image URLs → mine: alert description + observability context.)*

### Node 2 — Guardrails Input Check
Sends an HTTP POST to the Guardrails service on EC2 with the raw input text.
Receives `{passed, flags, reason}`. If `passed=false`, the flow branches to
the rejection path. If `passed=true`, continues to node 3.
*(Checks: is this a genuine operational alert — rejecting junk, off-topic text, and prompt-injection attempts.)*

### Node 3 — IF (Pass/Fail Branch)
Standard n8n IF node on `{{ $json.passed }}` (boolean). Failure → rejection
response node, returning the guardrail's `{passed, flags, reason}` verbatim
to the UI. Success → Information Extractor.

### Node 4 — Information Extractor (Prompt Surface #1)
n8n Information Extractor node backed by Gemini. Extracts structured fields:
**affected service, environment/region, error signature, severity indicators,
time window, and any mentioned customer impact.**
*(Course fields: property type, location, price, rooms, features, certifications → 1:1 field-count crosswalk.)*

**Prompt Engineering Task — Node 4:** systemPromptTemplate must instruct the
model to extract only facts present in the alert text, handle missing fields
gracefully (null, never guessed), and return consistent types. 5 documented
iterations.

### Node 5 — AI Agent Node (Prompt Surface #2)
n8n AI Agent node (GPT-4o/Gemini). Receives the extracted fields and context.
Dispatches tool calls to the three EC2 services: **RAG (similar past
incidents), Predictor (incident classification), LangGraph (triage
reasoning).**
*(Course: RAG, Image Analyser, LangGraph → the Predictor replaces the Image Analyser.)*

**Prompt Engineering Task — Node 5:** agent role = **senior incident
commander** (course: senior property analyst). Define the three tools and the
structured JSON output. Tool-description quality determines correct tool
selection. 5 iterations.

### Node 6 — LLM Chain (Prompt Surface within the flow)
Receives the merged outputs from the AI Agent and the EC2 services. Produces
the final **incident brief** (Markdown) synthesizing three sources: the
extracted fields, the **classification + confidence** (course: image condition
scores), and the similar-incidents context from RAG — without inventing
missing information. Output structure enforced by a JSON schema in a
Structured Output Parser node, mirroring the brief model in `contracts.py`.

### Node 7 — Guardrails Output Check
Sends the generated brief to `/check/output`. Validates: **no fabricated
metrics or incident references, no invented root causes stated as fact, no
uncited claims** (course: no false legal claims / price guarantees). On fail →
flagged for human review, never returned to the UI as-is.

### Node 8 — Router
Reads `incident_class` from the structured output. Derives the 3-way routing
category and routes to the corresponding team webhook.
*(Course: residential {apartment, house, villa} vs commercial {office, retail, industrial} — a 6-value → team routing. Mine: 6 incident classes → 3 routing categories. The 6→3 mapping table lives only in this node.)*

---

## 4. EC2 Microservices — Incident Domain

All services: Python FastAPI, Dockerized, deployed on EC2 **t3.large**
(documented deviation: spec says t3.medium+; t3.large chosen for GGUF
inference headroom), exposed via HTTP on configured ports, security group
restricted to n8n egress IPs + dev machine.

### 4.1 Service 1 — RAG Service
| | |
|---|---|
| Endpoint | POST /query |
| Input | `{ "description": "<alert text>" }` |
| Output | `{ "similar_incidents": [...], "insight": "<generated text>" }` |
| Stack | LangChain · Llama.cpp · ChromaDB · HuggingFace embeddings |

Receives an alert description, embeds it (sentence-transformer), queries
ChromaDB for the top-3 most similar **past incidents**, injects the retrieved
context into a LangChain prompt, generates a short insight via Llama.cpp
(GGUF). Vector store pre-populated with **20+ synthetic incidents** (all 6
classes represented, ≥3 each) by a committed, seeded, idempotent script.

**Prompt Engineering Task — RAG (Surface #3):** the prompt must cite which
past incident each claim draws from (e.g. "per INC-042") and must not
fabricate details absent from the retrieved documents. 5 iterations on
structure, context-injection format, and phrasing.

### 4.2 Service 2 — Predictor *(crosswalk of the Image Analyser)*
| | |
|---|---|
| Endpoint | POST /predict |
| Input | `{ "alert_features": { ... } }` |
| Output | `{ "incident_class": "<one of 6>", "confidence": 0.91 }` |
| Stack | PyTorch · transfer learning (pretrained backbone, replaced head) |

Fine-tune a classifier over **6 incident classes** (course: 6 room types —
kitchen, bathroom, living room, bedroom, exterior, other). Synthetic labeled
dataset of **200+ samples**, seeded/reproducible, 70/15/15 split. Confidence
threshold below which the service returns `uncertain` (course: identical
requirement). Deliverables identical to spec: training script, .pth
checkpoint, augmentation/generation strategy documented, **test-set accuracy
reported** (target >75%).
*(Learning objective — train and serve a PyTorch model behind FastAPI — fully met; the input modality is tabular/log features instead of images, matching my production domain.)*

### 4.3 Service 3 — Guardrails Service
| | |
|---|---|
| Endpoints | POST /check/input · POST /check/output |
| Input | `{ "text": "<text to check>" }` |
| Output | `{ "passed": true/false, "flags": [...], "reason": "<if fail>" }` |
| Stack | NeMo Guardrails / custom rule engine · FastAPI · versioned rail configs |

**Documented schema deviation:** spec says `{pass, reason, safe_text}`; my
contract is `{passed, flags, reason}` — richer failure detail via `flags`,
locked in `contracts.py` with `extra="forbid"`, noted in deployment notes.

Input endpoint: genuine operational alert in the expected language — rejects
junk, offensive content, off-topic text, injection attempts. Output endpoint:
checks the generated brief for fabricated metrics, invented root causes, and
uncited claims. Deterministic rule floors override LLM judgments ("LLM
extracts; the service decides").

Flow (mirrors Figure 4): User Input → **Input Guardrail** (topic check ·
safety check) → FAIL: reject + explain / PASS → **LLM Processing** (n8n AI
Agent + EC2 services generate the brief) → **Output Guardrail** (no fabricated
facts · no uncited claims) → FAIL: block + flag for review / PASS → **Safe
Output** (validated incident brief returned).

**Prompt Engineering Task — Guardrails (Surface #4):** topic-detection prompt
+ policy-enforcement prompt. Minimize false positives (rejecting valid alerts,
target <5%) while blocking invalid inputs and unsafe outputs. 5 iterations
each.

### 4.4 Service 4 — LangGraph Agent
| | |
|---|---|
| Endpoint | POST /agent/run |
| Input | `{ "query": "<complex question about the incident>" }` |
| Output | `{ "answer": "...", "tools_used": [...], "reasoning_steps": [...] }` |
| Stack | LangGraph · FastAPI · Llama.cpp or external LLM API |

Stateful three-node graph: **planner** (decides tool sequence) → **tool
execution** (can invoke the RAG service and the Predictor) → **synthesiser**
(combines tool outputs). Designed for multi-step questions such as:
*"What remediation steps would bring this service back to SLO? Which of the
attached signals need attention first?"*
(course: renovation-to-condition-5 / which rooms need attention — same shape.)

**Prompt Engineering Task — LangGraph tool descriptions:** precise
descriptions for the RAG tool and the Predictor tool; vague descriptions cause
wrong-tool selection. 5 iterations against the same 10 benchmark queries.

---

## Deviations Register (for deployment notes — complete list)
1. Domain: real-estate listings → operational incidents (1:1 crosswalk, this document).
2. Image Analyser → Predictor: image modality → alert-feature modality; all ML learning objectives preserved.
3. Guardrail schema: `{pass, reason, safe_text}` → `{passed, flags, reason}`.
4. Instance: t3.medium+ → t3.large (GGUF inference headroom).
5. Extension implemented: Monitoring Dashboard → **Dynamic Grafana Dashboard Generator** (beyond spec: LLM-generated dashboard JSON per incident).
6. RAG I/O field names: `{query, limit}` → `{answer, citations, refused}` instead of `{description}` → `{similar_incidents, insight}` (`citations`≈similar incidents, `answer`≈insight; n8n already uses `{query, limit}`).
7. Predictor endpoint: `POST /analyse` instead of `/predict` (same ML objectives; frozen contract).
8. LangGraph response: validated `TriageReport` instead of `{answer, tools_used, reasoning_steps}` (richer incident brief; graph still planner→tools→synthesiser).
9. LangGraph specialists call RAG + Tools API; Predictor is invoked by n8n Node 5 (Incident Commander), not inside the LangGraph HTTP service.
10. RAG uses custom prompt assembly (`generator.py`) instead of LangChain chains; ChromaDB + sentence-transformers + optional llama.cpp GGUF remain the retrieval/generation stack.
11. Guardrails runtime: custom deterministic regex floor (+ `NoopPolicyEngine` seam for NeMo later) instead of NeMo Guardrails at Stage A.
