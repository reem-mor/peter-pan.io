"""LangGraph StateGraph triage brain — Planner → Specialists → Synthesiser.

Uses a real ``StateGraph`` with deterministic routing. RAG is invoked once per
incident inside the specialists node (ADR 0003 dedup rule).
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, TypedDict

import httpx
from langgraph.graph import END, StateGraph

_DATABASE_HINTS = ("postgres", "db", "database")
_INFRA_HINTS = ("redis", "ingress", "k8s", "node", "cache")
_SEVERITY_TO_P_LEVEL: dict[int, str] = {5: "P1", 4: "P2", 3: "P3", 2: "P4", 1: "P4"}
_DEFAULT_P_LEVEL = "P3"
_DEFAULT_CONFIDENCE = 0.9
_LOWERED_CONFIDENCE = 0.4
_HTTP_TIMEOUT_SECONDS = 3.0
_INSUFFICIENT_DATA = "insufficient data"
_DEFAULT_RECOMMENDED_STEPS: tuple[str, ...] = (
    "Review recent deploys for the affected service.",
    "Check service dashboards for correlated metrics.",
    "Confirm on-call ownership before taking action.",
)


class AgentState(TypedDict, total=False):
    incident: dict[str, Any]
    question: str | None
    plan_result: dict[str, Any]
    specialist_results: dict[str, Any]
    report: dict[str, Any]


def _categorize_service(service_name: str) -> str:
    name = (service_name or "").lower()
    if any(hint in name for hint in _DATABASE_HINTS):
        return "database"
    if any(hint in name for hint in _INFRA_HINTS):
        return "infra"
    return "application"


def _auth_headers() -> dict[str, str]:
    token = os.environ.get("PETER_SERVICES_TOKEN", "").strip()
    return {"Authorization": f"Bearer {token}"} if token else {}


def plan_node(state: AgentState) -> AgentState:
    incident = state["incident"]
    service_name = str(incident.get("service") or "")
    category = _categorize_service(service_name)
    return {
        **state,
        "plan_result": {"category": category, "specialists": [f"{category}_specialist"]},
    }


async def _call_rag(
    client: httpx.AsyncClient, rag_url: str, question: str
) -> dict[str, Any]:
    if not rag_url:
        return {"ok": False, "reason": _INSUFFICIENT_DATA, "answer": "", "citations": []}
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
        return {"ok": False, "reason": _INSUFFICIENT_DATA, "answer": "", "citations": []}


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
        return {"ok": True, **response.json()}
    except (httpx.HTTPError, ValueError):
        return {"ok": False, "reason": _INSUFFICIENT_DATA}


async def specialists_node(
    state: AgentState,
    *,
    rag_url: str,
    tools_url: str,
    client: httpx.AsyncClient,
) -> AgentState:
    incident = state["incident"]
    service_name = str(incident.get("service") or "")
    symptom = str(incident.get("symptom") or "")
    environment = str(incident.get("environment") or "")
    rag_question = state.get("question") or symptom or f"triage guidance for {service_name}"

    rag_result, service_context, similar_incidents = await asyncio.gather(
        _call_rag(client, rag_url, rag_question),
        _call_tool(
            client,
            tools_url,
            "service_context",
            {"service": service_name, "environment": environment},
        ),
        _call_tool(
            client,
            tools_url,
            "similar_incidents",
            {"service": service_name, "symptom": symptom},
        ),
    )
    return {
        **state,
        "specialist_results": {
            "rag": rag_result,
            "service_context": service_context,
            "similar_incidents": similar_incidents,
        },
    }


def _p_level_from_context(context: Any) -> tuple[str, float]:
    severity = context.get("severity") if isinstance(context, dict) else None
    if isinstance(severity, int) and severity in _SEVERITY_TO_P_LEVEL:
        return _SEVERITY_TO_P_LEVEL[severity], _DEFAULT_CONFIDENCE
    return _DEFAULT_P_LEVEL, _LOWERED_CONFIDENCE


def _p_level_from_incident(incident: dict[str, Any]) -> tuple[str, float]:
    p_level = incident.get("p_level")
    if p_level in {"P1", "P2", "P3", "P4"}:
        return str(p_level), _DEFAULT_CONFIDENCE
    return _p_level_from_context(incident.get("context"))


def _normalize_escalation_path(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in value.split("->") if part.strip()]
    return []


def _summarize_tool_result(tool_name: str, result: dict[str, Any]) -> str:
    if tool_name == "service_context":
        owner = result.get("owner_team", "unknown owner")
        return f"Tools API service_context: owner_team={owner}."
    if tool_name == "similar_incidents":
        incidents = result.get("similar_incidents", [])
        return f"Tools API similar_incidents: {len(incidents)} historical match(es) found."
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


def synthesise_node(state: AgentState) -> AgentState:
    incident = state["incident"]
    plan_result = state["plan_result"]
    specialist_results = state["specialist_results"]
    question = state.get("question")

    incident_id = str(incident.get("id") or "unknown")
    category = plan_result["category"]
    p_level, confidence = _p_level_from_incident(incident)
    guardrail_flags: list[str] = []

    service_context = specialist_results.get("service_context", {})
    if service_context.get("ok"):
        owner_team = service_context.get("owner_team", "unknown")
        escalation_path = _normalize_escalation_path(
            service_context.get("escalation_path", [])
        )
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
                "quote": "No grounded sources were available — insufficient data.",
            }
        ]
        guardrail_flags.append("insufficient_citations")

    symptom = str(incident.get("symptom") or "")
    service = incident.get("service") or "unknown-service"
    summary_parts = [f"Incident on {service}."]
    if symptom:
        summary_parts.append(f"Reported symptom: {symptom}.")
    if question:
        summary_parts.append(f"Triage question: {question}.")
    rag = specialist_results.get("rag", {})
    if rag.get("ok") and rag.get("answer"):
        summary_parts.append(f"RAG guidance: {rag['answer']}")
    else:
        summary_parts.append("RAG guidance unavailable (insufficient data).")

    similar = specialist_results.get("similar_incidents", {})
    probable_cause = "Probable cause not established — insufficient grounded data."
    if similar.get("ok") and similar.get("similar_incidents"):
        top = similar["similar_incidents"][0]
        cause = top.get("root_cause") if isinstance(top, dict) else None
        if cause:
            probable_cause = f"Likely related to a previously seen pattern: {cause}"[:1200]

    report = {
        "incident_id": incident_id,
        "category": category,
        "p_level": p_level,
        "summary": " ".join(summary_parts)[:1200],
        "probable_cause": probable_cause[:1200],
        "citations": citations,
        "owner_team": owner_team,
        "escalation_path": escalation_path,
        "recommended_steps": list(_DEFAULT_RECOMMENDED_STEPS),
        "confidence": confidence,
        "guardrail_flags": guardrail_flags,
        "generated_at": datetime.now(timezone.utc),
        "model_meta": {"provider": "langgraph", "stage": "A"},
    }
    return {**state, "report": report}


def _build_graph(
    *,
    rag_url: str,
    tools_url: str,
    client: httpx.AsyncClient,
):
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_node)

    async def specialists(state: AgentState) -> AgentState:
        return await specialists_node(state, rag_url=rag_url, tools_url=tools_url, client=client)

    graph.add_node("specialists", specialists)
    graph.add_node("synthesise", synthesise_node)
    graph.set_entry_point("plan")
    graph.add_edge("plan", "specialists")
    graph.add_edge("specialists", "synthesise")
    graph.add_edge("synthesise", END)
    return graph.compile()


async def run(
    incident: dict[str, Any],
    question: str | None,
    *,
    rag_url: str,
    tools_url: str,
    client: httpx.AsyncClient,
) -> dict[str, Any]:
    compiled = _build_graph(rag_url=rag_url, tools_url=tools_url, client=client)
    result = await compiled.ainvoke(
        {"incident": incident, "question": question},
    )
    return result["report"]
