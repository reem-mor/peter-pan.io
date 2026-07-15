---
name: rag-pipeline-internals
description: Use for any work inside the RAG service — embeddings, ChromaDB, Llama.cpp/GGUF inference, the pre-population script, or retrieval quality.
---

# RAG Pipeline Internals — Service 1

The chain (per the course spec, incident domain):
alert text → embed → ChromaDB top-3 → context-injected prompt → Llama.cpp
(GGUF) insight → `{similar_incidents, insight}` with citations.

## Embedder
- One sentence-transformers model for BOTH ingestion and query — mixing
  models silently breaks similarity. The model name is a single constant in
  the service config; the ingestion script imports it from there.
- Default: `all-MiniLM-L6-v2` (fast, CPU-fine on t3.large). Changing it =
  re-ingest everything; the collection stores which model built it (metadata)
  and the service refuses to query on mismatch.

## ChromaDB
- Persistent client, path from env (`CHROMA_PATH`), single collection
  `incidents`. Client + collection created once at startup (lifespan).
- Document = the incident text. Metadata per record:
  `{incident_id, incident_class, severity, service, resolution_summary}` —
  metadata is what makes a citation usable ("similar to INC-042, P2,
  payments-api").
- Query: top-3, return distances. If best distance is worse than a named
  threshold constant → return "no sufficiently similar incidents" honestly;
  never pad with weak matches.

## Pre-population (rubric deliverable: script + 20+ records)
- `scripts/populate_vector_store.py`: seeded, idempotent (deterministic
  `incident_id`s; re-run = upsert, not duplicates), reads synthetic incidents
  from a committed JSON — the data is reviewable, not generated on the fly.
- Coverage: all 6 incident classes represented, minimum 3 records each.
  Demo scenarios (payments-latency, disk-pressure, error-spike) must each
  have at least one strong deliberate match seeded — retrieval that finds
  nothing on camera kills the segment.

## Llama.cpp inference
- GGUF path from env (`GGUF_MODEL_PATH`), loaded once at startup via
  llama-cpp-python. Quantized 7B (Q4_K_M) fits t3.large RAM; document the
  exact file+quant in deployment notes.
- `n_ctx` sized to fit: system prompt + 3 retrieved docs + query. If context
  overflows, truncate the DOCUMENTS (oldest-resolution first), never the query.
- Generation: low temperature (0.2), bounded max_tokens (~300). The insight is
  grounded synthesis, not creative writing.

## The retrieval prompt (prompt surface #3 — versioned file)
Hard requirements the prompt must enforce (and tests must check):
1. Cite which incident each claim draws from: "(per INC-042)".
2. Only facts present in retrieved docs — no outside knowledge.
3. If retrieval is empty/weak, say so — never fabricate a similar incident.
The output guardrail strips uncited claims; a prompt that produces them fails
its own test suite.

## Tests (fixture-first, no live model in CI)
- Embedding + retrieval tests run against a tiny committed test collection.
- Llama.cpp calls mocked in CI; one manual smoke script
  (`scripts/smoke_rag.py`) exercises the real GGUF path on the box.
- Contract test: response validates against the shared model in contracts.py.
