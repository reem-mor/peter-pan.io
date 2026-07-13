"""Unit tests for the ChromaDB retrieval backend (no live chromadb required)."""

from __future__ import annotations

from typing import Any

import pytest

from rag_service.vector_rag import (
    EMBED_MODEL_METADATA_KEY,
    EMBED_MODEL_NAME,
    MAX_DISTANCE,
    ChromaRetriever,
    VectorHit,
    _excerpt,
    chroma_path,
    embedding_model_matches,
)


class _FakeEmbedder:
    def encode(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


class _FakeCollection:
    def __init__(self, metadata: dict[str, Any] | None = None) -> None:
        self.metadata = metadata or {EMBED_MODEL_METADATA_KEY: EMBED_MODEL_NAME}
        self._rows = [
            (
                "INC-101 orders-api error spike after release",
                {
                    "incident_id": "INC-101",
                    "incident_class": "error_rate_spike",
                    "severity": "P2",
                    "service": "orders-api",
                    "resolution_summary": "Rolled back release r3.",
                },
                0.2,
            ),
            (
                "postgres pool exhausted deadlocks",
                {
                    "incident_id": "INC-111",
                    "incident_class": "db_lock_contention",
                    "severity": "P1",
                    "service": "postgres-primary",
                    "resolution_summary": "Paused bulk import.",
                },
                0.9,
            ),
        ]

    def query(self, **kwargs: Any) -> dict[str, list]:
        n = int(kwargs.get("n_results", len(self._rows)))
        docs, metas, distances = zip(*self._rows[:n])
        return {
            "documents": [list(docs)],
            "metadatas": [list(metas)],
            "distances": [list(distances)],
        }


def test_excerpt_includes_citation_header():
    text = _excerpt(
        "orders-api 5xx surge",
        {
            "incident_id": "INC-101",
            "severity": "P2",
            "service": "orders-api",
            "resolution_summary": "Rollback.",
        },
    )
    assert "(per INC-101, P2, orders-api)" in text
    assert "Resolution: Rollback." in text


def test_embedding_model_matches_accepts_same_model():
    assert embedding_model_matches({"embedding_model": EMBED_MODEL_NAME}) is True


def test_embedding_model_matches_rejects_mismatch():
    assert embedding_model_matches({"embedding_model": "other-model"}) is False


def test_chroma_retriever_filters_weak_distances():
    retriever = ChromaRetriever(_FakeCollection(), _FakeEmbedder())
    hits = retriever.search("orders-api error rate", top_k=3)
    assert len(hits) == 1
    assert hits[0].doc_id == "INC-101"
    assert hits[0].source_type == "incident_history"
    assert hits[0].score == pytest.approx(0.8, abs=0.01)


def test_chroma_retriever_respects_top_k():
    collection = _FakeCollection()
    collection._rows = [
        ("a", {"incident_id": "A", "severity": "P3", "service": "x", "resolution_summary": ""}, 0.1),
        ("b", {"incident_id": "B", "severity": "P3", "service": "x", "resolution_summary": ""}, 0.15),
    ]
    retriever = ChromaRetriever(collection, _FakeEmbedder())
    hits = retriever.search("query", top_k=1)
    assert len(hits) == 1


def test_get_vector_retriever_returns_none_when_store_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "missing"))
    import rag_service.vector_rag as mod

    mod._cached.clear()
    assert mod.get_vector_retriever() is None


def test_get_vector_retriever_returns_none_on_model_mismatch(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path))
    import rag_service.vector_rag as mod

    mod._cached.clear()

    class _Client:
        def get_collection(self, name: str) -> _FakeCollection:
            return _FakeCollection(metadata={"embedding_model": "wrong"})

    class _chromadb:
        @staticmethod
        def PersistentClient(path: str) -> _Client:
            return _Client()

    class _ST:
        def __init__(self, name: str) -> None:
            pass

    monkeypatch.setitem(__import__("sys").modules, "chromadb", _chromadb)
    monkeypatch.setitem(
        __import__("sys").modules,
        "sentence_transformers",
        type("m", (), {"SentenceTransformer": _ST}),
    )
    assert mod.get_vector_retriever() is None


def test_chroma_path_default_under_data_dir():
    assert chroma_path().name == "chroma"


def test_vector_hit_is_frozen_dataclass():
    hit = VectorHit("doc", "id", "incident_history", "excerpt", 0.9)
    assert hit.score == 0.9
    assert MAX_DISTANCE == 0.8
