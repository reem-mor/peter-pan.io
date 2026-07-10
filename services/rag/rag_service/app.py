"""FastAPI app for the RAG microservice (Stage A: TF-IDF retrieval, extractive answers).

Retrieval is real TF-IDF cosine similarity over the corpus; the answer is
extractive (top passages stitched together) — no LLM call in Stage A
(BUILD_PLAN §3 RAG row). Answers are never returned without citations: below
``MIN_SCORE`` the service refuses instead of guessing.
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from rag_service.contracts import Citation
from rag_service.errors import QueryValidationError
from rag_service.local_rag import get_retriever
from rag_service.validators import validate_question

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
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="missing or invalid bearer token")


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

    hits = get_retriever().search(question, top_k=request.limit)
    if not hits:
        return QueryResponse(answer=REFUSAL_ANSWER, citations=[], refused=True)

    citations = [
        Citation(
            source_id=hit.doc_id, source_type=hit.source_type, quote=hit.excerpt[:500]
        )
        for hit in hits
    ]
    answer = "\n\n".join(hit.excerpt.strip() for hit in hits)[:MAX_ANSWER_CHARS]
    return QueryResponse(answer=answer, citations=citations, refused=False)
