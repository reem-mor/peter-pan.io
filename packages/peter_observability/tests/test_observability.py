"""Regression tests for correlation middleware control flow."""

from __future__ import annotations

import asyncio
import json
import logging

import pytest
from starlette.requests import Request
from starlette.responses import Response

from observability import (
    CORRELATION_HEADER,
    CorrelationMiddleware,
    _JsonFormatter,
    configure_logging,
    default_readiness,
)


def _request(path: str = "/test", correlation_id: str | None = None) -> Request:
    headers = []
    if correlation_id:
        headers.append(
            (CORRELATION_HEADER.lower().encode(), correlation_id.encode())
        )
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": headers,
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        }
    )


def _middleware() -> CorrelationMiddleware:
    async def unused_app(scope, receive, send):
        raise AssertionError("dispatch calls the injected call_next directly")

    return CorrelationMiddleware(unused_app)


def test_success_adds_correlation_header_and_logs_outcome(caplog):
    async def scenario() -> Response:
        async def call_next(_request: Request) -> Response:
            return Response(status_code=200)

        return await _middleware().dispatch(
            _request(correlation_id="corr-test-123"),
            call_next,
        )

    with caplog.at_level(logging.INFO):
        response = asyncio.run(scenario())

    assert response.headers[CORRELATION_HEADER] == "corr-test-123"
    record = next(record for record in caplog.records if record.message == "request completed")
    assert record.outcome == "ok"
    assert record.correlation_id == "corr-test-123"


def test_call_next_exception_propagates_original_error_without_unboundlocal(caplog):
    async def scenario() -> None:
        async def call_next(_request: Request) -> Response:
            raise RuntimeError("downstream failed")

        await _middleware().dispatch(_request(path="/boom"), call_next)

    with caplog.at_level(logging.INFO):
        with pytest.raises(RuntimeError, match="downstream failed"):
            asyncio.run(scenario())

    record = next(record for record in caplog.records if record.message == "request completed")
    assert record.outcome == "error"
    assert record.operation == "GET /boom"


def test_json_formatter_emits_structured_request_fields():
    formatter = _JsonFormatter("test-service")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request completed",
        args=(),
        exc_info=None,
    )
    record.correlation_id = "corr-1"
    record.operation = "GET /healthz"
    record.duration_ms = 1.25
    record.outcome = "ok"

    payload = json.loads(formatter.format(record))

    assert payload["service"] == "test-service"
    assert payload["correlation_id"] == "corr-1"
    assert payload["outcome"] == "ok"


def test_configure_logging_installs_json_formatter():
    root = logging.getLogger()
    existing_handlers = root.handlers[:]
    root.handlers.clear()
    try:
        configure_logging("configured-service")
        assert isinstance(root.handlers[0].formatter, _JsonFormatter)
    finally:
        root.handlers.clear()
        root.handlers.extend(existing_handlers)


def test_default_readiness_fails_closed_per_check():
    async def healthy() -> bool:
        return True

    async def broken() -> bool:
        raise RuntimeError("dependency unavailable")

    result = asyncio.run(default_readiness({"healthy": healthy, "broken": broken}))

    assert result == {
        "ready": False,
        "checks": {"healthy": True, "broken": False},
    }


def test_default_readiness_without_checks_is_ready():
    assert asyncio.run(default_readiness({})) == {"ready": True, "checks": {}}
