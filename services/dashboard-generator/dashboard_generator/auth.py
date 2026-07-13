"""Bearer-token auth — enforced only when PETER_SERVICES_TOKEN is set."""

from __future__ import annotations

import hmac
import os

from fastapi import Header, HTTPException


async def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.environ.get("PETER_SERVICES_TOKEN")
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing or invalid bearer token")
    provided = authorization.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="missing or invalid bearer token")
