"""Suite-wide isolation from developer authentication environment variables."""

import pytest


@pytest.fixture(autouse=True)
def _clear_service_token(monkeypatch):
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)
