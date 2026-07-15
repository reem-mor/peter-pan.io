"""PETER PAN Layer 1 — business logic module.

All non-Streamlit logic lives here so it can be unit-tested without a
running Streamlit server.  ``app.py`` imports from this module; tests import
it directly.

Vendored contracts: Signal (minimal subset). Per AGENTS.md, cross-service
imports are forbidden — the UI vendors only the fields it touches.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Vendored contracts (subset of docs/contracts/contracts.py)
# Only fields the UI reads or writes are included.  The pattern and enum
# constraints are copied verbatim from the canonical contract so that the
# UI always emits valid Signal JSON.
# ---------------------------------------------------------------------------


class Signal(BaseModel):
    """Minimal UI vendor of the canonical Signal contract."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^sig-[a-z0-9-]{8,}$")
    source: Literal["grafana", "webui", "github", "slack"] = "webui"
    kind: Literal["alert", "manual", "deploy_event", "complaint"] = "manual"
    received_at: datetime
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(default="", max_length=8000)
    service: str | None = None
    environment: str | None = None
    severity_hint: Literal["critical", "warning", "info"] | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)


class SubmissionResult(BaseModel):
    """Result of a webhook submission attempt."""

    model_config = ConfigDict(extra="allow")

    ok: bool
    status_code: int = 0
    detail: str = ""
    signal_id: str = ""
    body: dict[str, Any] | None = None
    kind: Literal[
        "triage_report",
        "rejected",
        "flagged_for_review",
        "suppressed",
        "predictor_invalid",
        "error",
        "unreachable",
        "misconfigured",
    ] = "error"


def classify_webhook_body(
    status_code: int, payload: dict[str, Any] | None
) -> tuple[str, bool]:
    """Map HTTP status + JSON body to a UI result kind and ok flag."""
    if payload is None:
        return "error", False

    status = str(payload.get("status") or "").lower()
    if status == "rejected" or payload.get("passed") is False:
        return "rejected", True  # handled path, not a transport failure
    if status == "flagged_for_review":
        return "flagged_for_review", True
    if status == "suppressed":
        return "suppressed", True
    if status == "predictor_invalid":
        return "predictor_invalid", True
    if status_code == 200 and (
        "category" in payload or "incident_id" in payload or "summary" in payload
    ):
        return "triage_report", True
    if status_code == 202 and isinstance(payload.get("report"), dict):
        return "flagged_for_review", True
    if 200 <= status_code < 300:
        return "triage_report", True
    return "error", False


def extract_triage_report(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the TriageReport object from a webhook payload when present."""
    if not isinstance(payload, dict):
        return None
    report = payload.get("report")
    if isinstance(report, dict) and (
        "incident_id" in report or "category" in report or "summary" in report
    ):
        return report
    if "incident_id" in payload or "category" in payload or "summary" in payload:
        return payload
    return None


# ---------------------------------------------------------------------------
# Grounded refusal — system prompt + off-topic guard
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are PETER PAN — a Site Reliability Engineering assistant for a regulated
online-gaming platform (multi-jurisdiction: UKGC / MGA / NJ-DGE).

Scope: SRE, incident response, runbook interpretation, service health, latency
and error-rate analysis, deployment risk, rollback reasoning, on-call escalation.

Rules you MUST follow:
1. Off-topic questions must be refused with exactly:
   "I'm scoped to SRE and incident response — that question is outside my domain."
2. NEVER invent commands, SLA values, MTTR targets, RTO/RPO, runbook steps, or
   service owners that were not provided in the conversation context.
3. Always cite your reasoning: "Based on the provided runbook…" or
   "Without runbook context I cannot confirm, but a common safe first step is…"
4. If confidence is low, say so explicitly. Do not state SLA percentages you
   were not given.
5. Recommended steps must be read-only / non-destructive.
6. Never suggest `DROP`, `DELETE`, `kubectl delete`, or similar destructive ops.
"""

_OFF_TOPIC_KEYWORDS: frozenset[str] = frozenset(
    {
        "recipe", "cook", "bake", "food", "sport", "joke", "weather",
        "translate", "poem", "story", "movie", "film", "music", "song",
        "celebrity", "politics", "religion", "invest", "stock", "crypto",
        "bitcoin", "ethereum", "tax", "accounting", "dating", "relationship",
        "medical", "doctor", "nutrition",
    }
)

OFF_TOPIC_REPLY = (
    "I'm scoped to SRE and incident response — that question is outside my domain."
)


def is_off_topic(query: str) -> bool:
    """Return True if the query contains an off-topic keyword."""
    lower = query.lower()
    return any(kw in lower for kw in _OFF_TOPIC_KEYWORDS)


# ---------------------------------------------------------------------------
# Signal helpers
# ---------------------------------------------------------------------------


def new_sig_id() -> str:
    """Generate a valid Signal ID: ``sig-<12 lowercase hex chars>``."""
    return f"sig-{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# LLM adapter — fixture LLM first, Ollama fallback
# ---------------------------------------------------------------------------


def call_fixture_llm(messages: list[dict[str, str]], base_url: str) -> str:
    """POST to an OpenAI-compatible /chat/completions endpoint (fixture LLM)."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload: dict[str, Any] = {
        "model": "peter-stage-a-fixture",
        "messages": messages,
        "stream": False,
    }
    headers: dict[str, str] = {}
    token = os.environ.get("PETER_SERVICES_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = httpx.post(url, json=payload, headers=headers, timeout=30.0)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_ollama(
    messages: list[dict[str, str]], base_url: str, model: str
) -> str:
    """POST to Ollama /api/chat endpoint."""
    url = f"{base_url.rstrip('/')}/api/chat"
    payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
    resp = httpx.post(url, json=payload, timeout=60.0)
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def chat_sync(
    messages: list[dict[str, str]],
    fixture_url: str = "",
    ollama_url: str = "",
    ollama_model: str = "llama3",
) -> str:
    """Try fixture LLM; fall back to Ollama.  Raises ``RuntimeError`` if both fail."""
    last_exc: Exception | None = None

    if fixture_url:
        try:
            return call_fixture_llm(messages, fixture_url)
        except Exception as exc:  # noqa: BLE001 — intentional fallback
            last_exc = exc

    if ollama_url:
        try:
            return call_ollama(messages, ollama_url, ollama_model)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc

    raise RuntimeError(
        f"All LLM backends unavailable. Last error: {last_exc}"
    ) from last_exc


# ---------------------------------------------------------------------------
# Webhook submission
# ---------------------------------------------------------------------------


def submit_signal(
    signal: Signal,
    webhook_url: str,
    secret: str = "",
    timeout_s: float = 180.0,
) -> SubmissionResult:
    """POST a validated Signal JSON to the n8n webhook.

    Returns a SubmissionResult describing success or failure; never raises.
    Parses JSON body when present so the UI can render TriageReport / rejects.
    """
    if not webhook_url:
        return SubmissionResult(
            ok=False,
            detail="PETER_UI_N8N_WEBHOOK_URL not configured",
            kind="misconfigured",
        )

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if secret:
        headers["X-Peter-Webhook-Secret"] = secret

    try:
        resp = httpx.post(
            webhook_url,
            json=signal.model_dump(mode="json", exclude_none=True),
            headers=headers,
            timeout=timeout_s,
        )
    except httpx.HTTPError as exc:
        return SubmissionResult(
            ok=False,
            detail=str(exc),
            signal_id=signal.id,
            kind="unreachable",
        )

    payload: dict[str, Any] | None = None
    try:
        parsed = resp.json()
        if isinstance(parsed, dict):
            payload = parsed
    except Exception:  # noqa: BLE001 — keep raw text in detail
        payload = None

    kind, ok = classify_webhook_body(resp.status_code, payload)
    if payload is None and resp.status_code < 400:
        kind, ok = "error", False

    detail = ""
    if payload is not None:
        detail = str(
            payload.get("reason")
            or payload.get("summary")
            or payload.get("detail")
            or ""
        )[:500]
    if not detail:
        detail = (resp.text or "")[:500]

    return SubmissionResult(
        ok=ok,
        status_code=resp.status_code,
        detail=detail,
        signal_id=signal.id,
        body=payload,
        kind=kind,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------


def check_health(url: str) -> tuple[str, str]:
    """Probe a /healthz endpoint.

    Returns ``(status, detail)`` where status is one of:
    ``"ok"`` | ``"degraded"`` | ``"down"`` | ``"unknown"``.
    """
    if not url:
        return "unknown", "not configured"
    try:
        resp = httpx.get(url, timeout=3.0)
        if resp.status_code == 200:
            try:
                body = resp.json()
                return "ok", body.get("status", "ok")
            except Exception:  # noqa: BLE001
                return "ok", "200"
        return "degraded", f"HTTP {resp.status_code}"
    except httpx.ConnectError:
        return "down", "connection refused"
    except httpx.TimeoutException:
        return "down", "timeout"
    except Exception as exc:  # noqa: BLE001
        return "down", str(exc)[:80]


def health_url(base: str, path: str = "/healthz") -> str:
    """Append *path* to *base* only when *base* is non-empty."""
    return f"{base.rstrip('/')}{path}" if base else ""
