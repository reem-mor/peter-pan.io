"""PETER PAN Layer 1 — business logic module.

All non-Streamlit logic lives here so it can be unit-tested without a
running Streamlit server.  ``app.py`` imports from this module; tests import
it directly.

Vendored contracts: Signal (minimal subset). Per AGENTS.md, cross-service
imports are forbidden — the UI vendors only the fields it touches.
"""

from __future__ import annotations

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
    payload: dict[str, Any] = {"model": "fixture", "messages": messages, "stream": False}
    resp = httpx.post(url, json=payload, timeout=30.0)
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
) -> SubmissionResult:
    """POST a validated Signal JSON to the n8n webhook.

    Returns a SubmissionResult describing success or failure; never raises.
    """
    if not webhook_url:
        return SubmissionResult(
            ok=False, detail="PETER_UI_N8N_WEBHOOK_URL not configured"
        )

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if secret:
        headers["X-Peter-Webhook-Secret"] = secret

    try:
        resp = httpx.post(
            webhook_url,
            json=signal.model_dump(mode="json"),
            headers=headers,
            timeout=10.0,
        )
        return SubmissionResult(
            ok=resp.status_code < 400,
            status_code=resp.status_code,
            detail=resp.text[:500],
            signal_id=signal.id,
        )
    except httpx.HTTPError as exc:
        return SubmissionResult(ok=False, detail=str(exc), signal_id=signal.id)


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
