"""Owner-team verification against the Tools API — fail-closed by design.

BUILD_PLAN §3 (GRD row): "no-invented-owners check real" — an LLM-proposed
``TriageReport.owner_team`` is never trusted on its own; it must be confirmed
against the Tools API.

Known contract gap (listed, not silently resolved — see AGENTS.md / ADR conventions):
the frozen ``TriageReport`` contract (``docs/contracts/contracts.py``) carries
``owner_team`` but not the originating ``service`` slug (that lives on the upstream
``Incident``, not the report). Until an ADR extends the contract, Stage A verifies
team *existence* via the Tools API's ``GET /teams`` route rather than team-owns-service.

Fail-closed: a missing ``PETER_TOOLS_URL``, a network error, a timeout, or any
response that doesn't affirmatively confirm the team all yield ``verified=False`` —
an owner is never assumed genuine.
"""

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
    client: httpx.AsyncClient,
    tools_url: str | None = None,
) -> bool:
    """Return True only if the Tools API lists ``owner_team`` as a real team.

    ``client`` is injected (rather than constructed here) so callers — and
    tests — can supply an ``httpx.AsyncClient`` backed by ``httpx.MockTransport``.
    """
    base_url = tools_url if tools_url is not None else os.environ.get("PETER_TOOLS_URL")
    if not base_url or not owner_team:
        return False

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
