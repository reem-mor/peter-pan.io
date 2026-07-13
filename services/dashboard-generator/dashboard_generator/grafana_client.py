"""Grafana HTTP client — datasource UID resolved once at startup."""

from __future__ import annotations

import logging
import os
from copy import deepcopy
from typing import Any, Protocol

import httpx

from dashboard_generator.validator import assert_valid_dashboard

logger = logging.getLogger(__name__)

DS_PLACEHOLDER = "$DS_UID"


class GrafanaPoster(Protocol):
    def post_dashboard(self, payload: dict[str, Any]) -> dict[str, Any]: ...


class GrafanaClient:
    """POST /api/dashboards/db with Bearer auth."""

    def __init__(self, base_url: str, token: str, datasource_uid: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._datasource_uid = datasource_uid

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def resolve_datasource_uid(self) -> str:
        return self._datasource_uid

    def substitute_datasource(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = deepcopy(payload)
        panels = body.get("dashboard", {}).get("panels", [])
        for panel in panels:
            ds = panel.get("datasource")
            if isinstance(ds, dict) and ds.get("uid") == DS_PLACEHOLDER:
                ds["uid"] = self._datasource_uid
        return body

    def post_dashboard(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = self.substitute_datasource(payload)
        assert_valid_dashboard(body)
        url = f"{self._base_url}/api/dashboards/db"
        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, headers=self._headers(), json=body)
        if response.status_code >= 400:
            raise RuntimeError(
                f"Grafana POST failed ({response.status_code}): {response.text[:300]}"
            )
        return response.json()


class FixtureGrafanaClient:
    """Test double — validates and returns a synthetic success body."""

    def __init__(self, datasource_uid: str = "prometheus-demo") -> None:
        self._datasource_uid = datasource_uid
        self.last_payload: dict[str, Any] | None = None

    def resolve_datasource_uid(self) -> str:
        return self._datasource_uid

    def substitute_datasource(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = deepcopy(payload)
        for panel in body.get("dashboard", {}).get("panels", []):
            ds = panel.get("datasource")
            if isinstance(ds, dict) and ds.get("uid") == DS_PLACEHOLDER:
                ds["uid"] = self._datasource_uid
        return body

    def post_dashboard(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = self.substitute_datasource(payload)
        assert_valid_dashboard(body)
        self.last_payload = body
        uid = body["dashboard"].get("uid") or "pp-generated"
        return {
            "url": f"/d/{uid}/incident-dashboard",
            "uid": uid,
            "status": "success",
        }


_cached_client: GrafanaPoster | None = None


def _fetch_prometheus_uid(base_url: str, token: str) -> str:
    url = f"{base_url.rstrip('/')}/api/datasources"
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url, headers=headers)
    if response.status_code >= 400:
        raise RuntimeError(f"Grafana datasources fetch failed: {response.status_code}")
    for item in response.json():
        if item.get("type") == "prometheus":
            return str(item["uid"])
    raise RuntimeError("no prometheus datasource found in Grafana")


def get_grafana_client() -> GrafanaPoster:
    """Cached client; fixture mode when GRAFANA_API_TOKEN is unset."""
    global _cached_client
    if _cached_client is not None:
        return _cached_client

    base_url = os.environ.get("GRAFANA_URL", "http://localhost:3000")
    token = os.environ.get("GRAFANA_API_TOKEN", "").strip()
    if not token:
        logger.info("GRAFANA_API_TOKEN unset — using fixture Grafana client")
        _cached_client = FixtureGrafanaClient()
        return _cached_client

    ds_uid = os.environ.get("GRAFANA_PROMETHEUS_UID", "").strip()
    if not ds_uid:
        try:
            ds_uid = _fetch_prometheus_uid(base_url, token)
            logger.info("resolved prometheus datasource uid: %s", ds_uid)
        except (httpx.HTTPError, RuntimeError, KeyError) as exc:
            logger.warning("datasource resolution failed (%s) — using placeholder", exc)
            ds_uid = "prometheus"

    _cached_client = GrafanaClient(base_url, token, ds_uid)
    return _cached_client


def reset_client_cache() -> None:
    global _cached_client
    _cached_client = None
