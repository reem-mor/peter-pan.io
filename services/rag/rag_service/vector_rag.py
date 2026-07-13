"""ChromaDB + sentence-transformers retrieval backend (rag-pipeline-internals).

Selected with ``PETER_VECTOR_BACKEND=chroma``; the TF-IDF retriever in
``local_rag.py`` stays the fixture-first default, and every failure mode here
(libraries not installed, store missing, embedding-model mismatch) degrades
back to it with a logged error — the demo path never depends on this backend.

Store layout (single source shared with ``scripts/populate_vector_store.py``):
persistent client at ``CHROMA_PATH``, one collection ``incidents``, documents
= incident text, metadata ``{incident_id, incident_class, severity, service,
resolution_summary}``. The collection records which embedding model built it;
querying with a different model is refused (silent mixing breaks similarity).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger(__name__)

# One model constant for BOTH ingestion and query; the populate script imports it.
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "incidents"
EMBED_MODEL_METADATA_KEY = "embedding_model"

# Cosine distance above this is not a grounded match: the caller refuses
# instead of padding with weak hits ("no sufficiently similar incidents").
MAX_DISTANCE = 0.8

_DEFAULT_CHROMA_PATH = Path(__file__).resolve().parent.parent / "data" / "chroma"


def chroma_path() -> Path:
    return Path(os.environ.get("CHROMA_PATH", str(_DEFAULT_CHROMA_PATH)))


@dataclass(frozen=True)
class VectorHit:
    """A retrieved incident — field names mirror ``local_rag.RetrievedChunk``
    so the query route treats both backends identically."""

    document: str
    doc_id: str
    source_type: str  # always incident_history for this collection
    excerpt: str
    score: float


class Embedder(Protocol):
    def encode(self, texts: list[str], **kwargs: Any) -> Any: ...


class ChromaRetriever:
    """Top-k similar-incident retrieval over the persistent collection.

    ``collection`` and ``embedder`` are injectable so unit tests run without
    chromadb/sentence-transformers installed; ``get_vector_retriever`` does
    the real wiring once per process.
    """

    def __init__(self, collection: Any, embedder: Embedder) -> None:
        self._collection = collection
        self._embedder = embedder

    def search(self, query: str, *, top_k: int = 3) -> list[VectorHit]:
        embedding = self._embedder.encode([query], normalize_embeddings=True)
        result = self._collection.query(
            query_embeddings=[list(map(float, embedding[0]))],
            n_results=max(1, top_k),
            include=["documents", "metadatas", "distances"],
        )
        hits: list[VectorHit] = []
        for doc, meta, distance in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            if distance > MAX_DISTANCE:
                continue
            incident_id = str(meta.get("incident_id", "unknown"))
            hits.append(
                VectorHit(
                    document=incident_id,
                    doc_id=incident_id,
                    source_type="incident_history",
                    excerpt=_excerpt(doc, meta),
                    score=round(1.0 - float(distance), 4),
                )
            )
        return hits


def _excerpt(document: str, metadata: dict[str, Any]) -> str:
    """Citation-ready excerpt: the metadata is what makes it usable
    ("similar to INC-042, P2, payments-api")."""
    header = (
        f"(per {metadata.get('incident_id', 'unknown')}, "
        f"{metadata.get('severity', '?')}, {metadata.get('service', '?')}) "
    )
    resolution = str(metadata.get("resolution_summary", "")).strip()
    body = document.strip()
    if resolution:
        body = f"{body} Resolution: {resolution}"
    return header + body


def embedding_model_matches(metadata: dict[str, Any] | None) -> bool:
    """True when the collection was built with the model this service queries
    with — silent model mixing breaks similarity, so a mismatch refuses."""
    return (metadata or {}).get(EMBED_MODEL_METADATA_KEY) == EMBED_MODEL_NAME


_cached: dict[str, ChromaRetriever | None] = {}


def get_vector_retriever() -> ChromaRetriever | None:
    """Real wiring, cached per process. ``None`` = backend unavailable
    (caller falls back to TF-IDF); the reason is logged once."""
    key = str(chroma_path())
    if key not in _cached:
        _cached[key] = _build_retriever(key)
    return _cached[key]


def _build_retriever(path: str) -> ChromaRetriever | None:
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.error(
            "PETER_VECTOR_BACKEND=chroma but chromadb/sentence-transformers "
            "are not installed — falling back to TF-IDF"
        )
        return None
    if not Path(path).is_dir():
        logger.error(
            "chroma store missing at %s (run scripts/populate_vector_store.py) "
            "— falling back to TF-IDF",
            path,
        )
        return None
    try:
        client = chromadb.PersistentClient(path=path)
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as exc:  # chromadb raises library-specific errors
        logger.error("failed to open chroma collection: %s — falling back", exc)
        return None
    if not embedding_model_matches(collection.metadata):
        logger.error(
            "embedding-model mismatch: collection built with %r, service uses %r "
            "— refusing to query (re-run the populate script)",
            (collection.metadata or {}).get(EMBED_MODEL_METADATA_KEY),
            EMBED_MODEL_NAME,
        )
        return None
    embedder = SentenceTransformer(EMBED_MODEL_NAME)
    return ChromaRetriever(collection, embedder)
