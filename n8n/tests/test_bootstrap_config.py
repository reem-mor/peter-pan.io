"""Fail-fast configuration checks for the privileged local n8n bootstrap."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT_PATH = Path(__file__).parents[2] / "scripts" / "bootstrap_n8n_local.py"


def _load_bootstrap():
    spec = importlib.util.spec_from_file_location("bootstrap_n8n_local", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_owner_password_is_required_before_network_access(monkeypatch):
    module = _load_bootstrap()
    monkeypatch.setattr(module, "OWNER_PASSWORD", "")
    monkeypatch.setattr(module, "SERVICES_TOKEN", "test-token")

    with pytest.raises(RuntimeError, match="N8N_OWNER_PASSWORD is required"):
        module.main()


def test_service_token_is_required_before_network_access(monkeypatch):
    module = _load_bootstrap()
    monkeypatch.setattr(module, "OWNER_PASSWORD", "test-password")
    monkeypatch.setattr(module, "SERVICES_TOKEN", "")
    monkeypatch.setattr(module, "WEBHOOK_SECRET", "test-webhook")

    with pytest.raises(RuntimeError, match="PETER_SERVICES_TOKEN is required"):
        module.main()


def test_webhook_secret_is_required_before_network_access(monkeypatch):
    module = _load_bootstrap()
    monkeypatch.setattr(module, "OWNER_PASSWORD", "test-password")
    monkeypatch.setattr(module, "SERVICES_TOKEN", "test-token")
    monkeypatch.setattr(module, "WEBHOOK_SECRET", "")

    with pytest.raises(RuntimeError, match="PETER_WEBHOOK_SECRET is required"):
        module.main()


def test_publish_workflow_uses_authenticated_rest_version():
    module = _load_bootstrap()
    calls: list[tuple[str, dict]] = []

    class FakeClient:
        def post(self, path, json):
            calls.append((path, json))
            return SimpleNamespace(
                status_code=200,
                text="ok",
                raise_for_status=lambda: None,
            )

    module._publish_workflow(
        FakeClient(),
        workflow_id="workflow-123",
        version_id="version-456",
    )

    assert calls == [
        (
            "/rest/workflows/workflow-123/activate",
            {"versionId": "version-456"},
        )
    ]
