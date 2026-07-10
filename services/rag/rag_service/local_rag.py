"""Pure-Python TF-IDF + keyword retriever for offline RAG.

Stage A deterministic stub (ADR 0001 / BUILD_PLAN §3 RAG row): retrieval is
real TF-IDF cosine similarity over the local JSON corpus, no network call.
It loads JSON corpus documents from ``corpus/``, splits them into
heading-delimited chunks, and ranks chunks against a query. Every hit
carries the source document id, its corpus doc_type (mapped to the
``Citation.source_type`` contract), and an excerpt so the caller can cite it.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from rag_service.kb_corpus import document_text, iter_corpus_json_paths, kb_root
from rag_service.validators import tokenize

_CORPUS_DIR = kb_root()

# Minimum cosine score for a chunk to count as a grounded retrieval. Below this
# the retriever reports no match so the caller can refuse instead of guessing.
MIN_SCORE = 0.22

# Corpus doc_type -> Citation.source_type (docs/contracts/contracts.py Citation).
SOURCE_TYPE_BY_DOC_TYPE: dict[str, str] = {
    "runbook": "runbook",
    "incident": "incident_history",
    "service": "service_doc",
}

RUNBOOK_PRIORITY_DOCS = {
    "orders_api_error_spike.json",
    "deployment_rollback.json",
    "redis_cache_degradation.json",
    "database_connectivity.json",
    "ingress_5xx.json",
}


@dataclass(frozen=True)
class RetrievedChunk:
    """A single ranked chunk of a corpus document."""

    document: str  # source filename, e.g. "database_connectivity.json"
    doc_id: str  # corpus doc_id, used as Citation.source_id
    source_type: str  # runbook | incident_history | service_doc
    excerpt: str
    score: float
    chunk_index: int


def _split_chunks(text: str) -> list[str]:
    """Split a markdown document into heading-delimited chunks."""
    lines = text.splitlines()
    chunks: list[str] = []
    buffer: list[str] = []
    for line in lines:
        if line.startswith("#") and buffer:
            chunk = "\n".join(buffer).strip()
            if chunk:
                chunks.append(chunk)
            buffer = [line]
        else:
            buffer.append(line)
    tail = "\n".join(buffer).strip()
    if tail:
        chunks.append(tail)
    # Fall back to the whole document if there were no headings.
    if not chunks and text.strip():
        chunks.append(text.strip())
    return chunks


class LocalRetriever:
    """TF-IDF retriever over the corpus JSON documents."""

    def __init__(self, *, runbook_dir: Path | None = None) -> None:
        self._dir = runbook_dir or _CORPUS_DIR
        self._documents: list[RetrievedChunk] = []
        self._chunk_tokens: list[list[str]] = []
        self._idf: dict[str, float] = {}
        self._chunk_vectors: list[dict[str, float]] = []
        self._load()

    @property
    def runbook_dir(self) -> Path:
        return self._dir

    def document_count(self) -> int:
        return len({c.document for c in self._documents})

    def _load(self) -> None:
        if not self._dir.is_dir():
            return
        raw_chunks: list[tuple[str, str, str, int, str]] = []
        for path in iter_corpus_json_paths(root=self._dir):
            doc = json.loads(path.read_text(encoding="utf-8-sig"))
            doc_id = str(doc.get("doc_id", path.stem))
            source_type = SOURCE_TYPE_BY_DOC_TYPE.get(
                str(doc.get("doc_type", "")), "service_doc"
            )
            text = document_text(doc)
            for idx, chunk in enumerate(_split_chunks(text)):
                raw_chunks.append((path.name, doc_id, source_type, idx, chunk))

        self._chunk_tokens = [tokenize(chunk) for *_, chunk in raw_chunks]
        self._documents = [
            RetrievedChunk(
                document=name,
                doc_id=doc_id,
                source_type=source_type,
                excerpt=chunk,
                score=0.0,
                chunk_index=idx,
            )
            for name, doc_id, source_type, idx, chunk in raw_chunks
        ]

        n_docs = len(self._chunk_tokens) or 1
        df: dict[str, int] = {}
        for tokens in self._chunk_tokens:
            for term in set(tokens):
                df[term] = df.get(term, 0) + 1
        self._idf = {
            term: math.log((n_docs + 1) / (freq + 1)) + 1.0 for term, freq in df.items()
        }
        self._chunk_vectors = [self._vectorize(tokens) for tokens in self._chunk_tokens]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        counts: dict[str, int] = {}
        for term in tokens:
            counts[term] = counts.get(term, 0) + 1
        vector = {
            term: (count / len(tokens)) * self._idf.get(term, 1.0)
            for term, count in counts.items()
        }
        norm = math.sqrt(sum(weight * weight for weight in vector.values()))
        if norm == 0:
            return {}
        return {term: weight / norm for term, weight in vector.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        smaller, larger = (a, b) if len(a) <= len(b) else (b, a)
        return sum(weight * larger.get(term, 0.0) for term, weight in smaller.items())

    def search(self, query: str, *, top_k: int = 4) -> list[RetrievedChunk]:
        """Return the top-k chunks ranked by TF-IDF cosine similarity."""
        query_vector = self._vectorize(tokenize(query))
        if not query_vector or not self._chunk_vectors:
            return []
        scored: list[RetrievedChunk] = []
        for chunk, vector in zip(self._documents, self._chunk_vectors):
            score = self._cosine(query_vector, vector)
            if chunk.document in RUNBOOK_PRIORITY_DOCS:
                score *= 1.4
            if score >= MIN_SCORE:
                scored.append(
                    RetrievedChunk(
                        document=chunk.document,
                        doc_id=chunk.doc_id,
                        source_type=chunk.source_type,
                        excerpt=chunk.excerpt,
                        score=round(score, 4),
                        chunk_index=chunk.chunk_index,
                    )
                )
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[: max(1, top_k)]


@lru_cache(maxsize=4)
def get_retriever(runbook_dir: str | None = None) -> LocalRetriever:
    """Cached retriever so the corpus is parsed once per process."""
    return LocalRetriever(runbook_dir=Path(runbook_dir) if runbook_dir else None)
