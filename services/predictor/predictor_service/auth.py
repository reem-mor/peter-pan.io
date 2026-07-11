"""Shared bearer-auth dependency for non-health routes.

Vendored per-service (AGENTS.md: no ``services.*`` cross-imports — each
service dir is a self-contained deployment unit). When ``PETER_SERVICES_TOKEN``
is unset, auth is disabled (Stage A local/dev default); when set, every route
that depends on ``require_bearer_token`` requires a matching ``Authorization:
Bearer <token>`` header.
"""

from __future__ import annotations

import hmac
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer_scheme = HTTPBearer(auto_error=False)


async def require_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    expected = os.environ.get("PETER_SERVICES_TOKEN")
    if not expected:
        return  # auth disabled — no token configured
    if credentials is None or not hmac.compare_digest(
        credentials.credentials, expected
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing bearer token",
        )
