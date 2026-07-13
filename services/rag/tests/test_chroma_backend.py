"""Chroma backend selection on the /query route."""

from __future__ import annotations

from rag_service.vector_rag import VectorHit


def test_query_uses_chroma_backend_when_configured(monkeypatch):
    import rag_service.app as app_mod
    from fastapi.testclient import TestClient

    class _ChromaStub:
        def search(self, query: str, top_k: int = 3):
            return [
                VectorHit(
                    document="INC-101",
                    doc_id="INC-101",
                    source_type="incident_history",
                    excerpt="(per INC-101, P2, orders-api) error spike",
                    score=0.91,
                )
            ]

    monkeypatch.setenv("PETER_VECTOR_BACKEND", "chroma")
    monkeypatch.setattr(app_mod, "get_vector_retriever", lambda: _ChromaStub())
    client = TestClient(app_mod.app)
    resp = client.post("/query", json={"query": "orders-api 5xx error rate after release"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is False
    assert body["citations"][0]["source_id"] == "INC-101"
    assert body["citations"][0]["source_type"] == "incident_history"
