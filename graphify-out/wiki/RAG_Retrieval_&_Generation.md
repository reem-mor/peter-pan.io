# RAG Retrieval & Generation

> 44 nodes · cohesion 0.07

## Key Concepts

- **vector_rag.py** (12 connections) — `services/rag/rag_service/vector_rag.py`
- **generator.py** (9 connections) — `services/rag/rag_service/generator.py`
- **get_vector_retriever()** (7 connections) — `services/rag/rag_service/vector_rag.py`
- **get_generator()** (6 connections) — `services/rag/rag_service/generator.py`
- **LlamaGenerator** (6 connections) — `services/rag/rag_service/generator.py`
- **ChromaRetriever** (6 connections) — `services/rag/rag_service/vector_rag.py`
- **_build_retriever()** (5 connections) — `services/rag/rag_service/vector_rag.py`
- **populate_vector_store.py** (4 connections) — `scripts/populate_vector_store.py`
- **smoke_rag.py** (4 connections) — `scripts/smoke_rag.py`
- **build_prompt()** (4 connections) — `services/rag/rag_service/generator.py`
- **CompletionModel** (4 connections) — `services/rag/rag_service/generator.py`
- **chroma_path()** (4 connections) — `services/rag/rag_service/vector_rag.py`
- **.search()** (4 connections) — `services/rag/rag_service/vector_rag.py`
- **Embedder** (4 connections) — `services/rag/rag_service/vector_rag.py`
- **embedding_model_matches()** (4 connections) — `services/rag/rag_service/vector_rag.py`
- **_excerpt()** (4 connections) — `services/rag/rag_service/vector_rag.py`
- **Any** (4 connections)
- **main()** (3 connections) — `scripts/populate_vector_store.py`
- **main()** (3 connections) — `scripts/smoke_rag.py`
- **_load()** (3 connections) — `services/rag/rag_service/generator.py`
- **.__init__()** (3 connections) — `services/rag/rag_service/vector_rag.py`
- **.encode()** (3 connections) — `services/rag/rag_service/vector_rag.py`
- **VectorHit** (3 connections) — `services/rag/rag_service/vector_rag.py`
- **load_seed()** (2 connections) — `scripts/populate_vector_store.py`
- **.__call__()** (2 connections) — `services/rag/rag_service/generator.py`
- *... and 19 more nodes in this community*

## Relationships

- [RAG Query API](RAG_Query_API.md) (4 shared connections)

## Source Files

- `scripts/populate_vector_store.py`
- `scripts/smoke_rag.py`
- `services/rag/rag_service/generator.py`
- `services/rag/rag_service/vector_rag.py`

## Audit Trail

- EXTRACTED: 128 (94%)
- INFERRED: 8 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*