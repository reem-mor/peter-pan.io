"""Local fixtures for GitHub, Slack, and team webhooks — zero external egress."""

from __future__ import annotations

import hmac
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException

SERVICE_NAME = "integration-stubs"
app = FastAPI(title="PETER PAN Integration Stubs", version="0.1.0")

_DELIVERIES: list[dict[str, Any]] = []


def _check_delivery_auth(
    webhook_secret: str | None,
    authorization: str | None,
) -> None:
    expected_webhook = os.environ.get("PETER_WEBHOOK_SECRET", "").strip()
    expected_service = os.environ.get("PETER_SERVICES_TOKEN", "").strip()
    if not expected_webhook and not expected_service:
        return
    if (
        expected_webhook
        and webhook_secret is not None
        and hmac.compare_digest(webhook_secret, expected_webhook)
    ):
        return
    if expected_service and authorization and authorization.startswith("Bearer "):
        provided = authorization.removeprefix("Bearer ").strip()
        if hmac.compare_digest(provided, expected_service):
            return
    raise HTTPException(status_code=401, detail="invalid delivery credentials")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/github/deployments")
async def github_deployments() -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "deployments": [
            {
                "repo": os.environ.get("PETER_GITHUB_REPO", "demo/shop-platform"),
                "sha": "abc123def456",
                "deployed_at": now,
                "service": "orders-api",
            }
        ]
    }


@app.post("/slack")
async def slack_stub(
    payload: dict[str, Any],
    x_peter_webhook_secret: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    _check_delivery_auth(x_peter_webhook_secret, authorization)
    _DELIVERIES.append({"channel": "slack", "payload": payload})
    return {"status": "accepted"}


@app.post("/review-queue", status_code=202)
async def review_queue(
    payload: dict[str, Any],
    x_peter_webhook_secret: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    _check_delivery_auth(x_peter_webhook_secret, authorization)
    _DELIVERIES.append({"channel": "review", "payload": payload})
    return {"status": "accepted", "queue": "human-review"}


@app.post("/teams/{team}")
async def team_webhook(
    team: str,
    payload: dict[str, Any],
    x_peter_webhook_secret: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    _check_delivery_auth(x_peter_webhook_secret, authorization)
    _DELIVERIES.append({"channel": f"team:{team}", "payload": payload})
    return {"status": "accepted", "team": team}


@app.get("/deliveries")
async def deliveries(
    x_peter_webhook_secret: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    _check_delivery_auth(x_peter_webhook_secret, authorization)
    return list(_DELIVERIES)


@app.delete("/deliveries")
async def clear_deliveries(
    x_peter_webhook_secret: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> dict[str, int]:
    _check_delivery_auth(x_peter_webhook_secret, authorization)
    count = len(_DELIVERIES)
    _DELIVERIES.clear()
    return {"cleared": count}
