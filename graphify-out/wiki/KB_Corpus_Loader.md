# KB Corpus Loader

> 14 nodes · cohesion 0.22

## Key Concepts

- **kb_corpus.py** (8 connections) — `services/rag/rag_service/kb_corpus.py`
- **iter_corpus_json_paths()** (5 connections) — `services/rag/rag_service/kb_corpus.py`
- **load_kb_document()** (5 connections) — `services/rag/rag_service/kb_corpus.py`
- **load_kb_manifest()** (5 connections) — `services/rag/rag_service/kb_corpus.py`
- **document_text()** (4 connections) — `services/rag/rag_service/kb_corpus.py`
- **Any** (3 connections)
- **Path** (3 connections)
- **kb_manifest.py** (3 connections) — `services/rag/rag_service/kb_manifest.py`
- **kb_root()** (2 connections) — `services/rag/rag_service/kb_corpus.py`
- **kb_sections()** (2 connections) — `services/rag/rag_service/kb_manifest.py`
- **Load the PETER PAN RAG corpus (JSON documents under ``corpus/``).  Self-contai** (1 connections) — `services/rag/rag_service/kb_corpus.py`
- **Yield narrative corpus document JSON files from the doc subdirectories only.** (1 connections) — `services/rag/rag_service/kb_corpus.py`
- **Text used for chunking / retrieval (title + body).** (1 connections) — `services/rag/rag_service/kb_corpus.py`
- **Knowledge base manifest grouped by doc_type, for listing/introspection.** (1 connections) — `services/rag/rag_service/kb_manifest.py`

## Relationships

- [Local TF-IDF Retriever](Local_TF-IDF_Retriever.md) (3 shared connections)
- [Escalation Service](Escalation_Service.md) (1 shared connections)

## Source Files

- `services/rag/rag_service/kb_corpus.py`
- `services/rag/rag_service/kb_manifest.py`

## Audit Trail

- EXTRACTED: 39 (89%)
- INFERRED: 5 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*