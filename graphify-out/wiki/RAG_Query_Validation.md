# RAG Query Validation

> 12 nodes · cohesion 0.20

## Key Concepts

- **validators.py** (6 connections) — `services/rag/rag_service/validators.py`
- **QueryValidationError** (5 connections) — `services/rag/rag_service/errors.py`
- **tokenize()** (5 connections) — `services/rag/rag_service/validators.py`
- **validate_question()** (5 connections) — `services/rag/rag_service/validators.py`
- **errors.py** (4 connections) — `services/rag/rag_service/errors.py`
- **Exception** (1 connections)
- **.__init__()** (1 connections) — `services/rag/rag_service/errors.py`
- **Domain errors for the RAG service.  This service no longer calls Bedrock direc** (1 connections) — `services/rag/rag_service/errors.py`
- **Raised when an incoming /query question fails validation.      Carries a ``cod** (1 connections) — `services/rag/rag_service/errors.py`
- **Pure question validation for the RAG /query endpoint.  Operator/destructive-ac** (1 connections) — `services/rag/rag_service/validators.py`
- **Extract searchable tokens (length > 1, not stopwords).** (1 connections) — `services/rag/rag_service/validators.py`
- **Return the trimmed question or raise QueryValidationError with a stable code.** (1 connections) — `services/rag/rag_service/validators.py`

## Relationships

- [RAG Query API](RAG_Query_API.md) (3 shared connections)
- [Local TF-IDF Retriever](Local_TF-IDF_Retriever.md) (3 shared connections)

## Source Files

- `services/rag/rag_service/errors.py`
- `services/rag/rag_service/validators.py`

## Audit Trail

- EXTRACTED: 27 (84%)
- INFERRED: 5 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*