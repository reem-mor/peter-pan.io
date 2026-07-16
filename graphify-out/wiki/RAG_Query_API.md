# RAG Query API

> 12 nodes · cohesion 0.24

## Key Concepts

- **app.py** (15 connections) — `services/rag/rag_service/app.py`
- **query()** (7 connections) — `services/rag/rag_service/app.py`
- **_search()** (5 connections) — `services/rag/rag_service/app.py`
- **Citation** (4 connections) — `docs/contracts/contracts.py`
- **QueryRequest** (4 connections) — `services/rag/rag_service/app.py`
- **QueryResponse** (4 connections) — `services/rag/rag_service/app.py`
- **BaseModel** (2 connections)
- **require_bearer_token()** (2 connections) — `services/rag/rag_service/app.py`
- **healthz()** (1 connections) — `services/rag/rag_service/app.py`
- **FastAPI app for the RAG microservice.  Retrieval backends (``PETER_VECTOR_BACK** (1 connections) — `services/rag/rag_service/app.py`
- **Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set.** (1 connections) — `services/rag/rag_service/app.py`
- **Backend-selected retrieval; chroma degrades to TF-IDF when unavailable     (mis** (1 connections) — `services/rag/rag_service/app.py`

## Relationships

- [RAG Retrieval & Generation](RAG_Retrieval_%26_Generation.md) (4 shared connections)
- [RAG Query Validation](RAG_Query_Validation.md) (3 shared connections)
- [Canonical Contracts](Canonical_Contracts.md) (2 shared connections)
- [RAG Service Contracts](RAG_Service_Contracts.md) (2 shared connections)
- [Local TF-IDF Retriever](Local_TF-IDF_Retriever.md) (2 shared connections)
- [LangGraph Agent Service](LangGraph_Agent_Service.md) (1 shared connections)
- [n8n Bootstrap & Demo Assets](n8n_Bootstrap_%26_Demo_Assets.md) (1 shared connections)

## Source Files

- `docs/contracts/contracts.py`
- `services/rag/rag_service/app.py`

## Audit Trail

- EXTRACTED: 38 (81%)
- INFERRED: 9 (19%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*