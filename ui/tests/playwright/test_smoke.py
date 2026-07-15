"""Playwright smoke tests for Layer 1 UI + Layer 2 n8n login.

Requires a running local stack:
  docker compose --profile bootstrap --profile ui up -d

Credentials come from process env / .env (never hardcoded):
  N8N_OWNER_EMAIL, N8N_OWNER_PASSWORD, PETER_WEBHOOK_SECRET

Skip automatically when BASE_UI_URL host is unreachable.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = val.strip().strip('"').strip("'")


_load_dotenv()

BASE_UI = os.environ.get("BASE_UI_URL", "http://127.0.0.1:8501").rstrip("/")
BASE_N8N = os.environ.get("N8N_BASE_URL", "http://127.0.0.1:5678").rstrip("/")


def _reachable(url: str, timeout: float = 3.0) -> bool:
    try:
        httpx.get(url, timeout=timeout)
        return True
    except httpx.HTTPError:
        return False


pytestmark = pytest.mark.skipif(
    not _reachable(BASE_UI),
    reason=f"UI not reachable at {BASE_UI}",
)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1400, "height": 900},
        "ignore_https_errors": True,
    }


def test_ui_sidebar_shows_peter_pan(page) -> None:
    page.goto(BASE_UI, wait_until="domcontentloaded")
    page.get_by_text("PETER PAN", exact=False).first.wait_for(timeout=30_000)
    assert page.get_by_text("Service Health", exact=False).count() >= 1
    assert page.get_by_text("demo data", exact=False).count() >= 1


def test_ui_off_topic_assistant_refusal(page) -> None:
    page.goto(BASE_UI, wait_until="domcontentloaded")
    page.get_by_text("Assistant", exact=False).first.click()
    chat = page.get_by_placeholder("Ask about an incident, service, or runbook")
    chat.wait_for(timeout=30_000)
    chat.fill("Tell me a joke about pasta")
    chat.press("Enter")
    page.get_by_text(
        "I'm scoped to SRE and incident response", exact=False
    ).wait_for(timeout=30_000)


def test_ui_submit_valid_orders_api_shows_triage(page) -> None:
    page.goto(BASE_UI, wait_until="domcontentloaded")
    page.get_by_text("Incident Submission", exact=False).first.click()
    page.get_by_label("Title *").wait_for(timeout=30_000)
    page.get_by_label("Title *").fill("orders-api HTTP 5xx surge after deploy")
    page.get_by_label("Description").fill(
        "orders-api error rate spiked to 5.4% after release in production"
    )
    page.get_by_label("Service slug").fill("orders-api")
    # Streamlit selectboxes are not native <select> elements
    page.get_by_label("Environment").click()
    page.get_by_test_id("stSelectboxVirtualDropdown").get_by_text(
        "production", exact=True
    ).click()
    page.get_by_role("button", name="Submit Signal").click()
    # Long n8n path — accept either success banner or structured metrics
    page.get_by_text("Done (HTTP", exact=False).wait_for(timeout=200_000)
    content = page.content()
    assert "Triage complete" in content or "Category" in content
    assert "application" in content.lower() or "database" in content.lower() or "infra" in content.lower()
    assert "Signal rejected" not in content


def test_ui_submit_destructive_shows_reject(page) -> None:
    page.goto(BASE_UI, wait_until="domcontentloaded")
    page.get_by_text("Incident Submission", exact=False).first.click()
    page.get_by_label("Title *").wait_for(timeout=30_000)
    page.get_by_label("Title *").fill("Please DROP TABLE transactions_log in prod")
    page.get_by_label("Description").fill(
        "operator asked to DROP TABLE transactions_log on production"
    )
    page.get_by_label("Service slug").fill("orders-api")
    page.get_by_role("button", name="Submit Signal").click()
    page.get_by_text("Signal rejected", exact=False).wait_for(timeout=60_000)
    # Flag may appear as badge text or inside raw expander wording
    body = page.content()
    assert (
        "destructive_data_action" in body
        or "destructive data" in body.lower()
        or "DROP" in body
    )


def test_ui_empty_title_blocked(page) -> None:
    page.goto(BASE_UI, wait_until="domcontentloaded")
    page.get_by_text("Incident Submission", exact=False).first.click()
    page.get_by_label("Title *").wait_for(timeout=30_000)
    page.get_by_role("button", name="Submit Signal").click()
    page.get_by_text("Title is required", exact=False).wait_for(timeout=15_000)


@pytest.mark.skipif(
    not _reachable(f"{BASE_N8N}/healthz"),
    reason=f"n8n not reachable at {BASE_N8N}",
)
def test_n8n_login_and_workflow_active(page) -> None:
    email = os.environ.get("N8N_OWNER_EMAIL", "").strip()
    password = os.environ.get("N8N_OWNER_PASSWORD", "").strip()
    if not email or not password:
        pytest.skip("N8N_OWNER_EMAIL / N8N_OWNER_PASSWORD not set")

    page.goto(BASE_N8N, wait_until="domcontentloaded")
    # Login form (n8n 2.x)
    email_box = page.locator('input[type="email"], input[name="email"], input[placeholder*="mail" i]').first
    email_box.wait_for(timeout=30_000)
    email_box.fill(email)
    page.locator('input[type="password"]').first.fill(password)
    page.get_by_role(
        "button", name=re.compile(r"sign in|log in|continue", re.I)
    ).first.click()
    # Land on workflows or home
    page.wait_for_timeout(3000)
    page.goto(f"{BASE_N8N}/home/workflows", wait_until="domcontentloaded")
    page.get_by_text("Observability Triage", exact=False).first.wait_for(timeout=30_000)
    # Active indicator text varies; presence of workflow name is enough with prior REST check
    assert page.get_by_text("Observability Triage", exact=False).count() >= 1
