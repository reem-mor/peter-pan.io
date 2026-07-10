"""Unit tests for owner_check.verify_owner_team — fail-closed on every edge case.

Uses httpx.MockTransport directly (no FastAPI involved) to mock the Tools API's
``GET /teams`` route. Driven with asyncio.run() to keep the test suite free of an
extra async-test-runner dependency (pytest-asyncio/anyio-pytest are not pinned in
requirements.txt).
"""

from __future__ import annotations

import asyncio

import httpx

from guardrails_service.owner_check import verify_owner_team


def _run(coro):
    return asyncio.run(coro)


async def _verify(handler, owner_team: str, tools_url: str | None) -> bool:
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        return await verify_owner_team(owner_team, client=client, tools_url=tools_url)


def test_returns_false_when_tools_url_missing() -> None:
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("should not call the Tools API without a URL")

    result = _run(_verify(handler, "App Platform", None))
    assert result is False


def test_returns_true_when_team_listed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/teams"
        return httpx.Response(
            200, json={"teams": ["App Platform", "Database Reliability", "Infra SRE"]}
        )

    result = _run(_verify(handler, "App Platform", "http://tools-api.test"))
    assert result is True


def test_returns_false_on_error_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"error": "teams unavailable"})

    result = _run(_verify(handler, "App Platform", "http://tools-api.test"))
    assert result is False


def test_returns_false_when_team_not_listed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"teams": ["Database Reliability", "Infra SRE"]}
        )

    result = _run(_verify(handler, "Ghost Team", "http://tools-api.test"))
    assert result is False


def test_returns_false_on_non_200_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "internal error"})

    result = _run(_verify(handler, "App Platform", "http://tools-api.test"))
    assert result is False


def test_returns_false_on_network_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("simulated connection failure", request=request)

    result = _run(_verify(handler, "App Platform", "http://tools-api.test"))
    assert result is False


def test_returns_false_on_non_json_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    result = _run(_verify(handler, "App Platform", "http://tools-api.test"))
    assert result is False


def test_returns_false_on_malformed_teams_value() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"teams": "App Platform"})

    result = _run(_verify(handler, "App Platform", "http://tools-api.test"))
    assert result is False


def test_sends_bearer_header_when_token_set(monkeypatch) -> None:
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "sekrit")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("Authorization") == "Bearer sekrit"
        return httpx.Response(200, json={"teams": ["App Platform"]})

    result = _run(_verify(handler, "App Platform", "http://tools-api.test"))
    assert result is True
