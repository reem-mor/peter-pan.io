# ADR 0002 — Model routing, memory, and storage decisions

- **Status:** accepted (2026-07-10)
- **Source:** [model-memory-db-rationale.md](../model-memory-db-rationale.md) (user-authored
  design rationale, adopted as canonical for Layer 4 and the storage seams).

## Decisions

1. **Models are routed by task profile** (Stage C targets; Stage A stays mock-first behind
   the OpenAI-compatible fixture seam — nodes/services never change, only credentials):
   - n8n Extractor (node 4): **Gemini 2.5 Flash** — *supersedes* BUILD_PLAN's Bedrock Haiku
     (extraction is high-volume/low-reasoning; Flash has native structured output in n8n).
   - n8n Incident Commander + Report Writer (nodes 5–6): **Claude Sonnet via Bedrock**
     (tool-calling reliability; one IAM-scoped credential instead of scattered API keys).
   - RAG generation (Layer 3 service): **Mistral 7B GGUF via llama.cpp** (local inference
     required; CPU-only EC2).
   - WebUI assistant (Layer 1): **Ollama Llama 3 8B** (local, multi-turn).
2. **Memory by shape:**
   - Triage agent: **no conversational memory** — each incident is a stateless, independent
     run; buffer memory would leak context across incidents (correctness bug, not feature).
   - WebUI assistant: **windowed buffer memory** (~6 turns, per session id).
   - Cross-incident recall: **RAG over the vector store**, never LLM memory.
3. **Storage by lifetime:**
   - Vector store: **ChromaDB first**, then migrate to **Supabase pgvector** with a
     precision@3 before/after benchmark (managed-vector-store extension).
   - System of record (incidents, approval audit trail, review queue): **PostgreSQL on the
     same Supabase instance** — one database, two schemas. Stage A keeps the deterministic
     SQLite audit stub; Postgres replaces it when Supabase lands (Stage C track).
   - **Redis only if a concrete ephemeral need appears** (session state, dedupe, rate
     limits) — no speculative infrastructure.

## Consequences

- BUILD_PLAN Layer 4 / n8n node-4 rows and the Stage C order now name Gemini Flash for
  extraction; the flow's sticky note and `n8n/README.md` updated to match.
- The Confluence→pgvector seam in the system diagram stays (pgvector confirmed); ChromaDB
  is an accepted intermediate step, not a diagram change.
