"""Vendored observability helpers — copy into each service package unchanged."""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

CORRELATION_HEADER = "X-Correlation-Id"


def configure_logging(service_name: str) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )
    logging.getLogger().handlers[0].setFormatter(
        _JsonFormatter(service_name)  # type: ignore[arg-type]
    )


class _JsonFormatter(logging.Formatter):
    def __init__(self, service_name: str) -> None:
        super().__init__()
        self._service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": self._service_name,
            "message": record.getMessage(),
        }
        for key in ("correlation_id", "operation", "duration_ms", "outcome"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, default=str)


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get(CORRELATION_HEADER) or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        start = time.perf_counter()
        outcome = "error"
        try:
            response = await call_next(request)
            outcome = "ok" if response.status_code < 500 else "error"
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logging.getLogger(__name__).info(
                "request completed",
                extra={
                    "correlation_id": correlation_id,
                    "operation": f"{request.method} {request.url.path}",
                    "duration_ms": duration_ms,
                    "outcome": outcome,
                },
            )
        response.headers[CORRELATION_HEADER] = correlation_id
        return response


async def default_readiness(checks: dict[str, Callable[[], Awaitable[bool]]]) -> dict[str, Any]:
    results: dict[str, bool] = {}
    for name, check in checks.items():
        try:
            results[name] = await check()
        except Exception:
            results[name] = False
    ready = all(results.values()) if results else True
    return {"ready": ready, "checks": results}
