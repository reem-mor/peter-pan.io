# PETER PAN — Model, Memory & Database Decisions
### The reasoning behind every AI/data choice in the n8n flow (for Alex)

The guiding principle: **match the model to the job, not the job to the biggest model.**
A triage pipeline has four *different* cognitive tasks. Using one giant model everywhere is
expensive, slow, and — importantly — hides the engineering judgment the rubric is grading.
Below is each decision and why it is the right one, not just a working one.

---

## 1 · Model routing — why three tiers, not one

| n8n node | Job it does | Model chosen | Why this model, not a bigger/smaller one |
|---|---|---|---|
| **Information Extractor** (Node 4) | Pull fixed fields from short alert text. No reasoning. | **Gemini 2.5 Flash** | Extraction is high-volume, low-IQ. Flash is fast + cheap and has native structured-output support in n8n. A "pro"/reasoning model here burns money and latency for zero quality gain — this runs on *every* signal. |
| **Triage Agent** (Node 5) | Decide *which tools to call* and in what order. | **Claude 3.5 Sonnet (Bedrock)** | Tool-calling reliability is the differentiator; a wrong-tool call is the #1 agent failure mode.
| **Report Writer** (Node 6) | Synthesise tool outputs into a strict-JSON TriageReport, no invention. | **Claude 3.5 Sonnet (Bedrock)** | Synthesis-under-constraints (cite or say "insufficient data") is a reasoning task; a small model drifts and hallucinates owners/runbooks. Sonnet + a Structured Output Parser guarantees schema-valid output. |
| **RAG generation** (EC2 service) | Turn retrieved runbook chunks into a short grounded insight. | **Mistral 7B GGUF via Llama.cpp** | Guideline *requires* local inference here. A Q4 GGUF runs on a CPU-only EC2 (no GPU cost) and 7B is plenty for "summarise these 3 chunks with citations." |
| **WebUI assistant** (local) | Conversational SRE Q&A sidebar. | **Ollama · Llama 3 8B** | Guideline requires a local Ollama model. 8B has the best instruction-following of the small local models and runs comfortably on my RTX 3060. |

**The one-sentence version for the teacher:** *"I route by task profile — cheap/fast models for
extraction, a strong tool-calling model for the agent and synthesis, and local models where the
spec demands on-prem inference — because that's how a real cost-and-latency-aware AI system is
built, and it shows I understand what each model tier is actually for."*

### Why NOT the uploaded workflow's choices
The uploaded flow used a heavyweight "pro"/`gpt-5.4`-class model on **all three** LLM nodes,
including extraction. That is the classic anti-pattern: paying reasoning-model prices for a
copy-fields-out-of-text task that Flash does identically. Downgrading Node 4 to Flash cuts the
per-run cost of the most-frequently-hit node by roughly an order of magnitude with no quality loss.

### Why Bedrock over raw OpenAI/Gemini for the reasoning nodes
Three reasons, in priority order: (1) **credential surface** — one IAM-scoped Bedrock credential
instead of scattering OpenAI keys, which fits the "never hardcode secrets, least privilege"
requirement; (2) **portfolio continuity** — Bedrock experience transfers directly to production incident workflows;
(3) **enterprise story** — a self-hostable/VPC product shouldn't depend on a consumer API key.
*(Deviation note for Alex: the guideline names Gemini/GPT-4o for the n8n LM nodes. n8n has a native
Bedrock Chat node, so this is a one-node swap, declared openly, not a hidden change.)*

---

## 2 · Memory — where it belongs and where it must NOT

The instinct is "add memory to the agent." For this pipeline that would be **wrong**, and being
able to say why is the point.

| Surface | Memory? | Reasoning |
|---|---|---|
| **Triage Agent (Node 5)** | **No conversational memory** | Each incident is a *stateless, independent* triage. Buffer/window memory would leak one incident's context into the next — a P1 DB outage bleeding into an unrelated latency blip. Determinism and isolation matter more than "memory" here. The agent gets everything it needs in one payload (extracted fields + context + metric ref). |
| **WebUI Ollama assistant** | **Yes — windowed buffer memory** | This *is* a conversation. The SRE asks a follow-up ("and what about the payments cluster?"). A short window-buffer memory (last ~6 turns, keyed by session ID) gives natural multi-turn Q&A. Bounded window, not infinite, to cap token cost. |
| **Cross-incident "memory"** | **Yes — but as RAG, not as LLM memory** | The system genuinely should remember *past incidents* — but that's durable, searchable knowledge, not a chat buffer. That belongs in the vector store (below), retrieved on demand, not stuffed into an agent's context window. |

**The teacher-facing insight:** *"Memory is not one thing. Conversation needs a rolling buffer;
cross-incident recall needs a vector database; and a per-incident triage agent needs neither —
adding memory there would be a correctness bug, not a feature."* That distinction is exactly the
kind of judgment the rubric rewards.

---

## 3 · Database / vector store — two stores, two jobs

| Store | Purpose | Choice | Why |
|---|---|---|---|
| **Vector store (RAG)** | Semantic recall of past incidents + runbook chunks | **ChromaDB → migrate to Supabase pgvector** | Start on ChromaDB (satisfies the guideline stack literally, zero setup). Migrate to pgvector because: (a) it's the *Managed Vector Store* optional extension = extra credit; (b) pgvector is one database for *both* vectors and relational incident metadata — no second system to run; (c) the migration + a precision@3 before/after benchmark is concrete evidence of engineering rigour. |
| **State / audit store** | Incident records, approval audit log, review-queue items, execution metadata | **PostgreSQL (same Supabase instance)** | The approval gate needs a durable, queryable audit trail (who approved what, when). n8n's execution store isn't a system of record. Reusing the Postgres that already backs pgvector means **one database, two schemas** — simplest thing that scales, no over-engineering. |
| **Short-term / session** | WebUI chat session memory, rate-limit counters, dedupe keys | **Redis** *(only if needed)* | Ephemeral, fast, TTL-based. Only added if the WebUI session memory or signal-deduplication actually needs it — otherwise the window-buffer memory node handles chat state and Redis stays out. Don't add infrastructure speculatively. |

**Why not a fancier managed vector DB (Pinecone/Weaviate) from day one:** the guideline lists
ChromaDB; jumping straight to Pinecone would (a) skip the graded ChromaDB deliverable and (b) add a
paid external dependency to a self-hostable product. pgvector keeps everything in-VPC, which is the
whole enterprise pitch. Pinecone is mentioned in docs as a "if we outgrow pgvector" future note —
honest about the ceiling without over-building now.

---

## 4 · Summary — the mental model to present

Three sentences that capture the whole architecture:

1. **Models by task:** fast/cheap for extraction, strong for reasoning & tool-calling, local where
   the spec (or privacy) demands — never one model for everything.
2. **Memory by shape:** a rolling buffer for conversation, a vector DB for cross-incident recall,
   and deliberately *no* memory on the stateless triage agent.
3. **Storage by lifetime:** pgvector for semantic history, Postgres for the durable audit trail,
   Redis only if a real ephemeral need appears — one database family, minimal moving parts.

Every choice is defensible as "simplest thing that is correct and scales," which is exactly the
engineering posture the project is grading.
