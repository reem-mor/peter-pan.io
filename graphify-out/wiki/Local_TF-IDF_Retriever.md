# Local TF-IDF Retriever

> 19 nodes · cohesion 0.16

## Key Concepts

- **LocalRetriever** (10 connections) — `services/rag/rag_service/local_rag.py`
- **local_rag.py** (8 connections) — `services/rag/rag_service/local_rag.py`
- **._load()** (8 connections) — `services/rag/rag_service/local_rag.py`
- **.search()** (6 connections) — `services/rag/rag_service/local_rag.py`
- **get_retriever()** (5 connections) — `services/rag/rag_service/local_rag.py`
- **RetrievedChunk** (4 connections) — `services/rag/rag_service/local_rag.py`
- **.__init__()** (3 connections) — `services/rag/rag_service/local_rag.py`
- **._vectorize()** (3 connections) — `services/rag/rag_service/local_rag.py`
- **Path** (3 connections)
- **_split_chunks()** (3 connections) — `services/rag/rag_service/local_rag.py`
- **._cosine()** (2 connections) — `services/rag/rag_service/local_rag.py`
- **.runbook_dir()** (2 connections) — `services/rag/rag_service/local_rag.py`
- **.document_count()** (1 connections) — `services/rag/rag_service/local_rag.py`
- **Pure-Python TF-IDF + keyword retriever for offline RAG.  Stage A deterministic** (1 connections) — `services/rag/rag_service/local_rag.py`
- **Return the top-k chunks ranked by TF-IDF cosine similarity.** (1 connections) — `services/rag/rag_service/local_rag.py`
- **Cached retriever so the corpus is parsed once per process.** (1 connections) — `services/rag/rag_service/local_rag.py`
- **A single ranked chunk of a corpus document.** (1 connections) — `services/rag/rag_service/local_rag.py`
- **Split a markdown document into heading-delimited chunks.** (1 connections) — `services/rag/rag_service/local_rag.py`
- **TF-IDF retriever over the corpus JSON documents.** (1 connections) — `services/rag/rag_service/local_rag.py`

## Relationships

- [KB Corpus Loader](KB_Corpus_Loader.md) (3 shared connections)
- [RAG Query Validation](RAG_Query_Validation.md) (3 shared connections)
- [RAG Query API](RAG_Query_API.md) (2 shared connections)

## Source Files

- `services/rag/rag_service/local_rag.py`

## Audit Trail

- EXTRACTED: 59 (92%)
- INFERRED: 5 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*