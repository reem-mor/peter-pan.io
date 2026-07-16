---
name: rag-evaluation
description: Use when working on PETER PAN's RAG service — retrieval quality, citation enforcement, no-context refusal, corpus ingestion, or the precision@3 benchmark. Trigger when editing services/rag/, the KB seed script, the frozen RAG eval set, or any citation-verification logic. Covers the grounding contract (cite or refuse, never fabricate), the retrieval-fallback safety floor, and how to measure retrieval quality.
---

# RAG Evaluation & Grounding

The RAG service answers `POST /query`: `{description}` → `{similar_incidents, runbook_refs, insight}`. Its one non-negotiable job: **ground every claim in a real KB entry, or refuse.** Invention is the failure mode that matters most.

## The grounding contract
1. **Cite or refuse.** Every `insight` and every `runbook_ref` must trace to a retrieved chunk. If retrieval returns nothing relevant, return an explicit **"not in KB"** refusal — never synthesize an answer from model priors.
2. **Citation substring validation.** A citation is only valid if the cited text actually appears in (or is a faithful paraphrase of) the retrieved chunk. Validate citations programmatically — don't trust the LLM's self-reported source.
3. **No fabricated IDs.** `runbook_refs` must be real KB document IDs present in the corpus manifest. A ref not in the manifest is a contract violation → drop it and flag.

## Retrieval safety floor (deterministic)
Keep deterministic retrieval (embedding similarity over the vector store) as the fallback path. The LLM re-ranks/synthesizes on top, but if the LLM layer fails or times out, deterministic top-k retrieval still returns cited chunks. The floor guarantees the service degrades to "here are the nearest KB entries" rather than to invention.

## Corpus discipline
- **Synthetic data only** — ≥25 synthetic runbooks + ≥30 synthetic incident reports, seeded via the KB pre-pop script. No real incidents, ever.
- **Idempotent ingestion.** Re-running the seed script must not duplicate documents. Dedup on a stable content hash / doc ID.
- **Stable manifest.** Maintain a chunk/document manifest so tests can assert on known IDs and so citation validation has a source of truth.

## Vector store adapters
ChromaDB is the default; pgvector is the "Managed Vector Store" path (disabled-by-default Supabase adapter). Both sit behind one retrieval interface — swap via config, not code changes. Validate with local fixtures/emulators, never a live account during build (fixture-first).

## Frozen eval set (10 queries)
Do NOT mutate mid-iteration — it's the pass-rate baseline.
- ~7 queries with a genuine KB match → assert correct retrieval + valid citation.
- ~3 queries with **no** KB match → assert the "not in KB" refusal fires (this is the anti-fabrication test).

## Metrics to persist
- **precision@3** — of the top-3 retrieved, how many are relevant. This is the headline benchmark, especially for the ChromaDB→pgvector comparison.
- **Citation validity rate** — % of returned citations that pass substring validation.
- **Refusal correctness** — on the no-match queries, did it refuse instead of inventing?

Persist metric outputs (don't just print) so runs are comparable across iterations and the pgvector-vs-Chroma benchmark is evidence-backed.

## Pipeline internals (migrated from rag-pipeline-internals)

- One embedder for ingest + query (`all-MiniLM-L6-v2` default); collection metadata stores
  the model name; refuse query on mismatch.
- Chroma persistent client (`CHROMA_PATH`), collection `incidents`, top-3 with distance
  threshold — never pad weak matches.
- Pre-pop: `scripts/populate_vector_store.py` — seeded, idempotent, all 6 classes ≥3 each.
- GGUF via `GGUF_MODEL_PATH` / llama-cpp-python; load once; low temperature; truncate docs
  not the query on context overflow. CI mocks Llama; `scripts/smoke_rag.py` for live GGUF.

## When editing here
- Never remove the "not in KB" refusal path to "improve" answer coverage — refusal *is* the feature.
- Never weaken citation validation to raise pass rate. Report real failures.
- Corpus changes → re-run ingestion idempotency check + precision@3.
