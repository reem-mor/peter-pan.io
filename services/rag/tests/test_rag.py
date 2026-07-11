"""Tests for the offline TF-IDF retriever and the /query endpoint.

Replaces the deleted app.local_agent.LocalRagClient (the old Flask chat
client) — grounding/citation behaviour now lives directly behind the FastAPI
/query route (rag_service.app).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from rag_service.app import REFUSAL_ANSWER, app
from rag_service.local_rag import MIN_SCORE, LocalRetriever, get_retriever

client = TestClient(app)


def test_retriever_indexes_corpus():
    r = get_retriever()
    assert r.runbook_dir.name == "corpus"
    assert r.document_count() >= 10


def test_search_returns_database_runbook_for_postgres_query():
    hits = get_retriever().search(
        "Postgres connection pool exhausted CPU high on production what is the runbook",
        top_k=3,
    )
    assert hits
    assert hits[0].document == "database_connectivity.json"
    assert hits[0].score > 0


def test_search_returns_orders_api_runbook():
    hits = get_retriever().search(
        "orders-api error rate spike after deployment checkout failing", top_k=3
    )
    assert any("orders_api_error_spike" in h.document for h in hits)


def test_retriever_empty_dir(tmp_path):
    empty = LocalRetriever(runbook_dir=tmp_path)
    assert empty.search("anything", top_k=3) == []


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "rag"}


def test_query_endpoint_returns_grounded_citations():
    resp = client.post(
        "/query",
        json={
            "query": "Postgres connection pool exhausted on production, what is the runbook?"
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is False
    assert body["citations"]
    assert body["citations"][0]["source_type"] in {
        "runbook",
        "incident_history",
        "service_doc",
    }
    assert body["answer"]


def test_query_endpoint_refuses_off_topic():
    resp = client.post(
        "/query", json={"query": "What is the best restaurant in Tokyo right now?"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is True
    assert body["citations"] == []
    assert body["answer"] == "insufficient data"


def test_query_endpoint_rejects_empty_query():
    resp = client.post("/query", json={"query": "   "})
    assert resp.status_code == 422


def test_query_endpoint_respects_limit():
    resp = client.post(
        "/query",
        json={
            "query": "orders-api error rate spike after deployment checkout failing",
            "limit": 1,
        },
    )
    assert resp.status_code == 200
    assert len(resp.json()["citations"]) <= 1


# ---------------------------------------------------------------------------
# Below-threshold / refusal boundary
# ---------------------------------------------------------------------------


def test_retriever_every_hit_score_at_or_above_min_score():
    """The MIN_SCORE filter must exclude sub-threshold chunks from every result."""
    hits = get_retriever().search(
        "Postgres connection pool exhausted high CPU production runbook", top_k=5
    )
    assert hits, "expected at least one hit for a grounded query"
    for hit in hits:
        assert hit.score >= MIN_SCORE, (
            f"chunk {hit.document!r} returned with score {hit.score:.4f} < MIN_SCORE={MIN_SCORE}"
        )


def test_retriever_returns_empty_list_for_zero_match_query():
    """Nonsense token strings have no corpus overlap → empty hit list."""
    hits = get_retriever().search("xyzzy frobozz grumblequartz snarglefoo", top_k=3)
    assert hits == []


def test_refusal_when_retriever_returns_empty(monkeypatch):
    """When the retriever produces no hits, /query must refuse (never guess)."""
    import rag_service.app as app_mod

    class _EmptyRetriever:
        def search(self, _query: str, top_k: int = 3):
            return []

    monkeypatch.setattr(app_mod, "get_retriever", lambda: _EmptyRetriever())
    resp = client.post("/query", json={"query": "orders-api latency spike"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is True
    assert body["citations"] == []
    assert body["answer"] == REFUSAL_ANSWER


def test_refusal_response_has_correct_contract_shape():
    """Verify the complete refused-response contract shape."""
    resp = client.post(
        "/query", json={"query": "What is the capital of Neptune?"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) >= {"answer", "citations", "refused"}
    assert body["refused"] is True
    assert isinstance(body["citations"], list)
    assert body["answer"] == REFUSAL_ANSWER


@pytest.mark.parametrize(
    ("query", "expected_refused"),
    [
        ("Postgres connection pool exhausted CPU high production runbook", False),
        ("xyzzy frobozz grumblequartz snarglefoo", True),
        ("best sushi restaurant in Tokyo midnight special offer", True),
    ],
)
def test_refusal_boundary_parametrized(query, expected_refused):
    resp = client.post("/query", json={"query": query})
    assert resp.status_code == 200
    assert resp.json()["refused"] == expected_refused


def test_query_requires_bearer_token_when_configured(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "secret-token")
    unauthorized = client.post(
        "/query", json={"query": "Postgres connection pool exhausted on production"}
    )
    assert unauthorized.status_code == 401

    authorized = client.post(
        "/query",
        json={"query": "Postgres connection pool exhausted on production"},
        headers={"Authorization": "Bearer secret-token"},
    )
    assert authorized.status_code == 200
