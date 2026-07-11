"""Owner-team verification against the Tools API — fail-closed by design."""

from __future__ import annotations

import os

import httpx

TIMEOUT_SECONDS = 3.0


def _auth_headers() -> dict[str, str]:
    token = os.environ.get("PETER_SERVICES_TOKEN", "").strip()
    return {"Authorization": f"Bearer {token}"} if token else {}


async def verify_owner_team(
    owner_team: str,
    *,
    service: str | None = None,
    environment: str | None = "production",
    client: httpx.AsyncClient,
    tools_url: str | None = None,
) -> bool:
    """Return True when owner_team is confirmed via Tools API.

    When ``service`` is provided, verify the owner matches ``service_context``.
    Otherwise fall back to team existence via ``GET /teams``.
    """
    base_url = tools_url if tools_url is not None else os.environ.get("PETER_TOOLS_URL")
    if not base_url or not owner_team:
        return False

    if service:
        try:
            response = await client.post(
                f"{base_url.rstrip('/')}/tools/service_context",
                json={"service": service, "environment": environment or "production"},
                headers=_auth_headers(),
                timeout=TIMEOUT_SECONDS,
            )
        except httpx.HTTPError:
            return False
        if response.status_code != 200:
            return False
        try:
            body = response.json()
        except ValueError:
            return False
        expected = (body.get("owner_team") or "").strip()
        return bool(expected) and expected == owner_team

    try:
        response = await client.get(
            f"{base_url.rstrip('/')}/teams",
            headers=_auth_headers(),
            timeout=TIMEOUT_SECONDS,
        )
    except httpx.HTTPError:
        return False

    if response.status_code != 200:
        return False

    try:
        body = response.json()
    except ValueError:
        return False

    if not isinstance(body, dict) or body.get("error"):
        return False

    teams = body.get("teams")
    if not isinstance(teams, list):
        return False
    return owner_team in teams
