"""Stage A deterministic skeleton of the Planner -> Specialists -> Synthesiser
triage brain (BUILD_PLAN §3, LangGraph agent row).

This module is a plain-function pipeline, **not yet a LangGraph graph** —
building the real ``StateGraph`` with conditional routing is the next work
item once the Stage A services are wired end-to-end (BUILD_PLAN §3 lists
"graph topology real" as the target; this skeleton only gets the
deterministic-floor rules right first). What's here already enforces the
contract's guardrail rules: ``owner_team``/``escalation_path`` only ever come
from the Tools API, never invented by a model; ``p_level`` comes from a
deterministic severity mapping, not an LLM; ``citations`` is always
non-empty (schema-enforced by ``TriageReport``).

Category (``infra`` / ``database`` / ``application``) is derived from the
incident's service name with the same deterministic rules as the Predictor
service's ``category.py`` — duplicated here on purpose (AGENTS.md: no
``services.*`` cross-imports; every service dir is self-contained and talks
to the others over HTTP only).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx

# ---------------------------------------------------------------------------
# Deterministic category mapping (duplicated from predictor_service/category.py
# by design — see module docstring).
# ---------------------------------------------------------------------------

_DATABASE_HINTS = ("postgres", "db", "database")
_INFRA_HINTS = ("redis", "ingress", "k8s", "node", "cache")


def _categorize_service(service_name: str) -> str:
    name = (service_name or "").lower()
    if any(hint in name for hint in _DATABASE_HINTS):
        return "database"
    if any(hint in name for hint in _INFRA_HINTS):
        return "infra"
    return "application"


# ---------------------------------------------------------------------------
# Deterministic severity -> p_level mapping (BUILD_PLAN §3: "p_level ...
# deterministic code in the Predictor/Tools API, the LLM only proposes").
# ---------------------------------------------------------------------------

_SEVERITY_TO_P_LEVEL: dict[int, str] = {5: "P1", 4: "P2", 3: "P3", 2: "P4", 1: "P4"}
_DEFAULT_P_LEVEL = "P3"
_DEFAULT_CONFIDENCE = 0.9
_LOWERED_CONFIDENCE = 0.4  # no severity signal available -> defaulted, lower confidence

_HTTP_TIMEOUT_SECONDS = 3.0
_INSUFFICIENT_DATA = "insufficient data"


def _auth_headers() -> dict[str, str]:
    token = os.environ.get("PETER_SERVICES_TOKEN", "").strip()
    return {"Authorization": f"Bearer {token}"} if token else {}


# Deterministic, read-only/safe recommended steps (never destructive — the
# contract's own comment: "read-only/safe steps only").
_DEFAULT_RECOMMENDED_STEPS: tuple[str, ...] = (
    "Review recent deploys for the affected service.",
    "Check service dashboards for correlated metrics.",
    "Confirm on-call ownership before taking action.",
)


def plan(incident: dict[str, Any]) -> dict[str, Any]:
    """Planner node: pick the category + specialist list for this incident.

    Category is derived deterministically from ``incident["service"]`` — no
    LLM involved (see module docstring).
    """
    service_name = str(incident.get("service") or "")
    category = _categorize_service(service_name)
    return {"category": category, "specialists": [f"{category}_specialist"]}


async def _call_rag(
    client: httpx.AsyncClient, rag_url: str, question: str, service: str
) -> dict[str, Any]:
    if not rag_url:
        return {
            "ok": False,
            "reason": _INSUFFICIENT_DATA,
            "answer": "",
            "citations": [],
        }
    try:
        response = await client.post(
            f"{rag_url}/query",
            json={"query": question, "limit": 3},
            headers=_auth_headers(),
            timeout=_HTTP_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "ok": True,
            "answer": data.get("answer", ""),
            "citations": data.get("citations", []),
        }
    except (httpx.HTTPError, ValueError):
        return {
            "ok": False,
            "reason": _INSUFFICIENT_DATA,
            "answer": "",
            "citations": [],
        }


async def _call_tool(
    client: httpx.AsyncClient, tools_url: str, tool_name: str, payload: dict[str, Any]
) -> dict[str, Any]:
    if not tools_url:
        return {"ok": False, "reason": _INSUFFICIENT_DATA}
    try:
        response = await client.post(
            f"{tools_url}/tools/{tool_name}",
            json=payload,
            headers=_auth_headers(),
            timeout=_HTTP_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return {"ok": True, **data}
    except (httpx.HTTPError, ValueError):
        return {"ok": False, "reason": _INSUFFICIENT_DATA}


async def run_specialists(
    incident: dict[str, Any],
    plan_result: dict[str, Any],
    question: str | None,
    *,
    rag_url: str,
    tools_url: str,
    client: httpx.AsyncClient,
) -> dict[str, Any]:
    """Specialists node: call RAG + Tools API for grounding context.

    Graceful degradation on failure/timeout/missing config — every call is
    flagged ``{"ok": False, "reason": "insufficient data"}`` instead of
    raising, so a down dependency never breaks triage, only lowers confidence
    and grounding.
    """
    service_name = str(incident.get("service") or "")
    symptom = str(incident.get("symptom") or "")
    environment = str(incident.get("environment") or "")
    rag_question = question or symptom or f"triage guidance for {service_name}"

    rag_result = await _call_rag(client, rag_url, rag_question, service_name)
    service_context = await _call_tool(
        client,
        tools_url,
        "service_context",
        {"service": service_name, "environment": environment},
    )
    similar_incidents = await _call_tool(
        client,
        tools_url,
        "similar_incidents",
        {"service": service_name, "symptom": symptom},
    )
    return {
        "rag": rag_result,
        "service_context": service_context,
        "similar_incidents": similar_incidents,
    }


def _p_level_from_context(context: Any) -> tuple[str, float]:
    severity = context.get("severity") if isinstance(context, dict) else None
    if isinstance(severity, int) and severity in _SEVERITY_TO_P_LEVEL:
        return _SEVERITY_TO_P_LEVEL[severity], _DEFAULT_CONFIDENCE
    return _DEFAULT_P_LEVEL, _LOWERED_CONFIDENCE


def _summarize_tool_result(tool_name: str, result: dict[str, Any]) -> str:
    if tool_name == "service_context":
        owner = result.get("owner_team", "unknown owner")
        return f"Tools API service_context: owner_team={owner}."
    if tool_name == "similar_incidents":
        incidents = result.get("similar_incidents", [])
        return (
            f"Tools API similar_incidents: {len(incidents)} historical match(es) found."
        )
    return f"Tools API {tool_name} responded."


def _build_citations(specialist_results: dict[str, Any]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []

    rag = specialist_results.get("rag", {})
    for citation in rag.get("citations", []) or []:
        if isinstance(citation, dict) and {"source_id", "source_type", "quote"} <= set(
            citation.keys()
        ):
            citations.append(citation)

    for tool_name in ("service_context", "similar_incidents"):
        result = specialist_results.get(tool_name, {})
        if result.get("ok"):
            citations.append(
                {
                    "source_id": f"tool:{tool_name}",
                    "source_type": "tool_result",
                    "quote": _summarize_tool_result(tool_name, result)[:500],
                }
            )
    return citations


def _build_summary(
    incident: dict[str, Any], specialist_results: dict[str, Any], question: str | None
) -> str:
    service = incident.get("service") or "unknown-service"
    symptom = incident.get("symptom") or ""
    parts = [f"Incident on {service}."]
    if symptom:
        parts.append(f"Reported symptom: {symptom}.")
    if question:
        parts.append(f"Triage question: {question}.")
    rag = specialist_results.get("rag", {})
    if rag.get("ok") and rag.get("answer"):
        parts.append(f"RAG guidance: {rag['answer']}")
    else:
        parts.append("RAG guidance unavailable (insufficient data).")
    return " ".join(parts)[:1200]


def _build_probable_cause(specialist_results: dict[str, Any]) -> str:
    similar = specialist_results.get("similar_incidents", {})
    if similar.get("ok") and similar.get("similar_incidents"):
        top = similar["similar_incidents"][0]
        cause = top.get("root_cause") if isinstance(top, dict) else None
        if cause:
            return f"Likely related to a previously seen pattern: {cause}"[:1200]
    return "Probable cause not established — insufficient grounded data for this incident."[
        :1200
    ]


def synthesise(
    incident: dict[str, Any],
    plan_result: dict[str, Any],
    specialist_results: dict[str, Any],
    question: str | None,
) -> dict[str, Any]:
    """Synthesiser node: build the dict that must validate as ``TriageReport``.

    Deterministic-floor rules enforced here: ``owner_team``/``escalation_path``
    only ever copied from a successful Tools API ``service_context`` call
    (else "unknown"/[] plus a guardrail flag); ``p_level`` from
    ``_p_level_from_context``, never model output; ``citations`` always
    non-empty (falls back to a flagged placeholder citation if both RAG and
    Tools totally failed).
    """
    incident_id = str(incident.get("id") or "unknown")
    category = plan_result["category"]
    p_level, confidence = _p_level_from_context(incident.get("context"))

    guardrail_flags: list[str] = []

    service_context = specialist_results.get("service_context", {})
    if service_context.get("ok"):
        owner_team = service_context.get("owner_team", "unknown")
        escalation_path = list(service_context.get("escalation_path", []))
    else:
        owner_team = "unknown"
        escalation_path = []
        guardrail_flags.append("owner_unverified")

    citations = _build_citations(specialist_results)
    if not citations:
        citations = [
            {
                "source_id": "tool:none",
                "source_type": "tool_result",
                "quote": "No grounded sources were available (RAG and Tools API both "
                "unreachable/unconfigured) — insufficient data.",
            }
        ]
        guardrail_flags.append("insufficient_citations")

    return {
        "incident_id": incident_id,
        "category": category,
        "p_level": p_level,
        "summary": _build_summary(incident, specialist_results, question),
        "probable_cause": _build_probable_cause(specialist_results),
        "citations": citations,
        "owner_team": owner_team,
        "escalation_path": escalation_path,
        "recommended_steps": list(_DEFAULT_RECOMMENDED_STEPS),
        "confidence": confidence,
        "guardrail_flags": guardrail_flags,
        "generated_at": datetime.now(timezone.utc),
        "model_meta": {"provider": "deterministic-skeleton", "stage": "A"},
    }


async def run(
    incident: dict[str, Any],
    question: str | None,
    *,
    rag_url: str,
    tools_url: str,
    client: httpx.AsyncClient,
) -> dict[str, Any]:
    """Planner -> Specialists -> Synthesiser, in sequence."""
    plan_result = plan(incident)
    specialist_results = await run_specialists(
        incident,
        plan_result,
        question,
        rag_url=rag_url,
        tools_url=tools_url,
        client=client,
    )
    return synthesise(incident, plan_result, specialist_results, question)
