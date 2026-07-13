"""Dashboard Generator — fixture-first Grafana POST service (Session A, port 8008).

``POST /dashboard`` loads a committed scenario fixture (or accepts validated
custom JSON), substitutes the Prometheus datasource UID, validates against
``fixtures/dashboards/metrics_catalog.json``, and POSTs to Grafana
``/api/dashboards/db``. Live LLM JSON generation is blocked to Session D —
this path is deterministic fixtures only.
"""

from __future__ import annotations

import os
from typing import Any, Literal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from dashboard_generator.auth import require_bearer_token
from dashboard_generator.fixtures_loader import KNOWN_SCENARIOS, load_fixture
from dashboard_generator.grafana_client import get_grafana_client
from dashboard_generator.validator import DashboardValidationError, assert_valid_dashboard

SERVICE_NAME = "dashboard-generator"

app = FastAPI(title="PETER PAN Dashboard Generator")


class DashboardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: Literal[
        "orders-api-error-spike",
        "postgres-pool-pressure",
        "shop-web-latency",
        "disk-pressure",
    ]
    incident_id: str | None = Field(default=None, min_length=1, max_length=64)
    overwrite: bool = False


class DashboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dashboard_url: str
    uid: str
    panels_count: int


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.post(
    "/dashboard",
    response_model=DashboardResponse,
    dependencies=[Depends(require_bearer_token)],
)
async def create_dashboard(request: DashboardRequest) -> DashboardResponse:
    try:
        payload = load_fixture(request.scenario)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if request.incident_id:
        dash = payload.setdefault("dashboard", {})
        title = str(dash.get("title", "INCIDENT"))
        if " — " in title:
            dash["title"] = f"INCIDENT {request.incident_id} — {title.split(' — ', 1)[1]}"
        else:
            dash["title"] = f"INCIDENT {request.incident_id} — {title}"

    payload["overwrite"] = request.overwrite

    try:
        assert_valid_dashboard(payload)
    except DashboardValidationError as exc:
        raise HTTPException(
            status_code=422, detail={"code": "invalid_dashboard", "message": str(exc)}
        ) from exc

    client = get_grafana_client()
    try:
        result = client.post_dashboard(payload)
    except (DashboardValidationError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502, detail={"code": "grafana_error", "message": str(exc)}
        ) from exc

    uid = str(result.get("uid") or payload["dashboard"].get("uid", ""))
    url_path = str(result.get("url", f"/d/{uid}"))
    base = os.environ.get("GRAFANA_URL", "http://localhost:3000").rstrip("/")
    dashboard_url = url_path if url_path.startswith("http") else f"{base}{url_path}"
    panels = payload.get("dashboard", {}).get("panels", [])

    return DashboardResponse(
        dashboard_url=dashboard_url,
        uid=uid,
        panels_count=len(panels) if isinstance(panels, list) else 0,
    )


@app.get("/scenarios")
async def list_scenarios() -> dict[str, Any]:
    return {"scenarios": sorted(KNOWN_SCENARIOS)}
