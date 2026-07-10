"""Ingestion Service — accepts, validates, normalizes and forwards Signals.

BUILD_PLAN §3 (Ingestion API row): entry point of the system, "real" in
Stage A — it's just validation + forward to the n8n webhook. FastAPI parses
and validates the request body against the vendored ``Signal`` contract
automatically (422 with field-level detail on failure); this module only
adds the deterministic service-slug normalization and the forward-to-n8n
step, with graceful degradation when n8n isn't reachable/configured.
"""

from __future__ import annotations

import os

import httpx
from fastapi import Depends, FastAPI

from .auth import require_bearer_token
from .contracts import Signal

SERVICE_NAME = "ingestion"

app = FastAPI(title="PETER PAN Ingestion Service")

_FORWARD_TIMEOUT_SECONDS = 5.0
_FORWARD_ATTEMPTS = 2  # initial attempt + 1 retry


def _normalize_service_slug(service: str) -> str:
    """Lowercase, spaces -> dashes. Deterministic, no other transformation."""
    return service.strip().lower().replace(" ", "-")


def _build_client() -> httpx.AsyncClient:
    """Factory so tests can monkeypatch in an ``httpx.MockTransport`` client
    without touching real network I/O."""
    return httpx.AsyncClient(timeout=_FORWARD_TIMEOUT_SECONDS)


async def _forward_to_n8n(signal: Signal, url: str) -> int:
    """POST the validated Signal JSON to the n8n webhook. One retry on
    transport-level failure (timeout, connection error); the last error is
    re-raised for the caller to turn into a degraded (forwarded=false) reply.
    """
    payload = signal.model_dump(mode="json")
    last_exc: httpx.HTTPError | None = None
    async with _build_client() as client:
        for _attempt in range(_FORWARD_ATTEMPTS):
            try:
                response = await client.post(url, json=payload)
                return response.status_code
            except httpx.HTTPError as exc:  # noqa: PERF203 — retry loop is intentional
                last_exc = exc
    assert last_exc is not None  # for type checkers; loop always sets it on failure
    raise last_exc


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "service": SERVICE_NAME}


@app.post("/signals", status_code=202, dependencies=[Depends(require_bearer_token)])
async def create_signal(signal: Signal) -> dict:
    if signal.service:
        signal.service = _normalize_service_slug(signal.service)

    n8n_url = os.environ.get("N8N_WEBHOOK_URL")
    if not n8n_url:
        return {"forwarded": False, "reason": "n8n webhook not configured"}

    try:
        status_code = await _forward_to_n8n(signal, n8n_url)
    except httpx.HTTPError as exc:
        return {
            "forwarded": False,
            "reason": f"n8n webhook unreachable: {exc}",
            "signal_id": signal.id,
        }

    return {"forwarded": True, "signal_id": signal.id, "n8n_status": status_code}
