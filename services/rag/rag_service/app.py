"""FastAPI app for the RAG microservice.

Retrieval backends (``PETER_VECTOR_BACKEND``): ``tfidf`` (default,
fixture-first — real TF-IDF cosine similarity over the corpus) or ``chroma``
(``vector_rag.py`` — ChromaDB + sentence-transformers over the populated
incident store, degrading back to TF-IDF if unavailable). The answer is
extractive (top passages stitched together) unless a GGUF model is configured
via ``GGUF_MODEL_PATH`` (``generator.py``), in which case a grounded llama.cpp
insight replaces it. Answers are never returned without citations: with no
grounded hits the service refuses instead of guessing.
"""

from __future__ import annotations

import hmac
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from rag_service.contracts import Citation
from rag_service.errors import QueryValidationError
from rag_service.generator import get_generator
from rag_service.local_rag import get_retriever
from rag_service.validators import validate_question
from rag_service.vector_rag import get_vector_retriever

SERVICE_NAME = "rag"
REFUSAL_ANSWER = "insufficient data"
MAX_ANSWER_CHARS = 1500

app = FastAPI(title="PETER PAN RAG Service")


class QueryRequest(BaseModel):
    query: str
    limit: int = Field(default=3, ge=1, le=10)


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    refused: bool


async def require_bearer_token(
    authorization: str | None = Header(default=None),
) -> None:
    """Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set."""
    expected = os.environ.get("PETER_SERVICES_TOKEN")
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing or invalid bearer token")
    provided = authorization.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="missing or invalid bearer token")


def _search(question: str, limit: int):
    """Backend-selected retrieval; chroma degrades to TF-IDF when unavailable
    (missing libs/store or embedding-model mismatch — logged in vector_rag)."""
    if os.environ.get("PETER_VECTOR_BACKEND", "tfidf") == "chroma":
        retriever = get_vector_retriever()
        if retriever is not None:
            return retriever.search(question, top_k=limit)
    return get_retriever().search(question, top_k=limit)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.post(
    "/query", response_model=QueryResponse, dependencies=[Depends(require_bearer_token)]
)
async def query(request: QueryRequest) -> QueryResponse:
    try:
        question = validate_question(request.query)
    except QueryValidationError as exc:
        raise HTTPException(
            status_code=422, detail={"code": exc.code, "message": exc.message}
        ) from exc

    hits = _search(question, request.limit)
    if not hits:
        return QueryResponse(answer=REFUSAL_ANSWER, citations=[], refused=True)

    citations = [
        Citation(
            source_id=hit.doc_id, source_type=hit.source_type, quote=hit.excerpt[:500]
        )
        for hit in hits
    ]
    answer = "\n\n".join(hit.excerpt.strip() for hit in hits)[:MAX_ANSWER_CHARS]
    generator = get_generator()
    if generator is not None:
        insight = generator.generate(question, [hit.excerpt for hit in hits])
        if insight:
            answer = insight[:MAX_ANSWER_CHARS]
    return QueryResponse(answer=answer, citations=citations, refused=False)
