"""OpenAI-compatible Fixture LLM for Stage A n8n mock seam."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import time
from typing import Any, Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

SERVICE_NAME = "fixture-llm"
app = FastAPI(title="PETER PAN Fixture LLM", version="0.1.0")
logger = logging.getLogger("uvicorn.error")

TaskKind = Literal["extract", "agent", "synthesis", "rag_generate", "assistant"]


class ChatMessage(BaseModel):
    role: str
    content: str | None = None
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class ChatCompletionRequest(BaseModel):
    model: str = "peter-stage-a-fixture"
    messages: list[ChatMessage]
    response_format: dict[str, Any] | None = None
    temperature: float = 0.0
    tools: list[dict[str, Any]] = Field(default_factory=list)
    tool_choice: Any | None = None
    stream: bool = False


class ResponsesRequest(BaseModel):
    model: str = "peter-stage-a-fixture"
    input: str | list[Any]
    instructions: str | None = None
    temperature: float = 0.0


def _response_input_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(
            text for item in value if (text := _response_input_text(item))
        )
    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"]
        if "content" in value:
            return _response_input_text(value["content"])
    return ""


def _responses_messages(payload: ResponsesRequest) -> list[ChatMessage]:
    messages: list[ChatMessage] = []
    if payload.instructions:
        messages.append(ChatMessage(role="system", content=payload.instructions))
    if isinstance(payload.input, str):
        messages.append(ChatMessage(role="user", content=payload.input))
        return messages
    for item in payload.input:
        if isinstance(item, dict):
            role = str(item.get("role", "user"))
            content = _response_input_text(item.get("content", item))
        else:
            role = "user"
            content = _response_input_text(item)
        if content:
            messages.append(ChatMessage(role=role, content=content))
    return messages


def _detect_task(messages: list[ChatMessage]) -> TaskKind:
    blob = "\n".join(m.content or "" for m in messages).lower()
    extractor_markers = (
        "extract structured incident facts",
        "affected_metric",
        "mentioned_deploys",
    )
    if "extract" in blob and any(marker in blob for marker in extractor_markers):
        return "extract"
    if "triage report" in blob or "structured output" in blob or "json schema" in blob:
        return "synthesis"
    if "incident commander" in blob or "tool" in blob and "rag" in blob:
        return "agent"
    if "extract" in blob or "never infer severity" in blob:
        return "extract"
    if "sre assistant" in blob or "off-topic" in blob:
        return "assistant"
    if "citation" in blob or "runbook" in blob:
        return "rag_generate"
    return "extract"


def _fixture_id(messages: list[ChatMessage]) -> str:
    digest = hashlib.sha256(
        json.dumps([m.model_dump() for m in messages], sort_keys=True).encode()
    ).hexdigest()[:12]
    return f"fix-{digest}"


def _extract_response(messages: list[ChatMessage]) -> str:
    user = next((m.content or "" for m in reversed(messages) if m.role == "user"), "")
    service = ""
    normalized = user.lower()
    known_services = {
        "postgres-primary": ("postgres-primary", "postgres"),
        "shop-web": ("shop-web",),
        "orders-api": ("orders-api",),
        "payments-api": ("payments-api",),
        "redis-cache": ("redis-cache", "redis"),
        "k8s-ingress": ("k8s-ingress", "ingress"),
    }
    matches = [
        (normalized.index(alias), canonical)
        for canonical, aliases in known_services.items()
        for alias in aliases
        if alias in normalized
    ]
    if matches:
        service = min(matches)[1]
    environment = (
        "production"
        if "production" in normalized or "prod" in normalized
        else ("staging" if "staging" in normalized else "")
    )
    affected_metric = next(
        (
            metric
            for metric in ("error rate", "latency", "connections", "cpu", "memory")
            if metric in normalized
        ),
        "",
    )
    error_signature = "5xx" if "5xx" in normalized else ""
    customer_impact = (
        "Users are affected."
        if "users" in normalized or "checkout" in normalized
        else ""
    )
    mentioned_deploys = "recent deploy" if "deploy" in normalized else ""
    return json.dumps(
        {
            "service": service,
            "environment": environment,
            "started_at": "",
            "symptom": user[:200] or "elevated error rate",
            "affected_metric": affected_metric,
            "error_signature": error_signature,
            "customer_impact": customer_impact,
            "mentioned_deploys": mentioned_deploys,
        }
    )


def _commander_evidence(messages: list[ChatMessage]) -> dict[str, Any] | None:
    marker = "Commander findings:"
    for message in reversed(messages):
        content = message.content or ""
        if marker not in content:
            continue
        candidate = content.split(marker, 1)[1].lstrip()
        try:
            parsed, _end = json.JSONDecoder().raw_decode(candidate)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _predictor_policy(messages: list[ChatMessage]) -> dict[str, Any] | None:
    """Parse the deterministic predictor policy the flow injects into the prompt.

    The 6→3 class-to-category mapping lives only in the n8n flow (Apply
    Predictor Policy); this fixture copies routing_category from the policy,
    exactly as the Write TriageReport system message instructs the model to.
    """
    marker = "Predictor policy:"
    for message in reversed(messages):
        content = message.content or ""
        if marker not in content:
            continue
        candidate = content.split(marker, 1)[1].lstrip()
        try:
            parsed, _end = json.JSONDecoder().raw_decode(candidate)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _tool_grounded_report(
    messages: list[ChatMessage], evidence: dict[str, Any]
) -> dict[str, Any]:
    blob = "\n".join(message.content or "" for message in messages)
    incident_match = re.search(r"\binc-[a-z0-9-]{8,}\b", blob.lower())
    service_match = re.search(r'"service"\s*:\s*"([^"]+)"', blob)
    incident_id = incident_match.group(0) if incident_match else "inc-fixture001"
    service = service_match.group(1) if service_match else "unknown-service"

    predictor = evidence.get("predictor", {})
    deep = evidence.get("langgraph", {})
    retrieval = evidence.get("rag", deep)
    owner_context = evidence.get("service_context", deep)
    flags: list[str] = []

    severity = int(predictor.get("severity", 0) or 0)
    p_level = {5: "P1", 4: "P2", 3: "P3", 2: "P4", 1: "P4"}.get(
        severity, deep.get("p_level", "P3")
    )
    incident_class = predictor.get("incident_class")
    policy = _predictor_policy(messages) or {}
    category = policy.get("routing_category")
    if category not in {"infra", "database", "application"}:
        raise ValueError(
            "predictor_policy.routing_category is missing or unroutable; "
            "routing policy must stop before synthesis"
        )

    citations = retrieval.get("citations", [])
    if not isinstance(citations, list) or not citations:
        citations = [
            {
                "source_id": "tool:unavailable",
                "source_type": "tool_result",
                "quote": "insufficient data",
            }
        ]
        flags.append("insufficient_citations")

    owner_team = owner_context.get("owner_team") or "unknown"
    escalation_path = owner_context.get("escalation_path", [])
    if isinstance(escalation_path, str):
        escalation_path = [
            part.strip() for part in escalation_path.split("->") if part.strip()
        ]
    if owner_team == "unknown":
        flags.append("owner_unverified")

    return {
        "incident_id": incident_id,
        "category": category,
        "p_level": p_level,
        "summary": f"Tool-grounded fixture synthesis for {service}.",
        "probable_cause": deep.get("probable_cause")
        or retrieval.get("answer")
        or "Tool evidence requires human analysis.",
        "citations": citations,
        "owner_team": owner_team,
        "escalation_path": escalation_path if isinstance(escalation_path, list) else [],
        "recommended_steps": deep.get("recommended_steps")
        or [
            f"Review current health metrics for {service}.",
            "Compare the signal with recent deployment evidence.",
        ],
        "confidence": float(predictor.get("confidence") or deep.get("confidence") or 0.5),
        "guardrail_flags": sorted(set(flags)),
        "generated_at": "2026-07-10T12:05:00Z",
        "model_meta": {
            "provider": "fixture",
            "model": "peter-stage-a-fixture",
            "predictor_incident_class": str(incident_class),
            "predictor_severity": str(severity or ""),
            "evidence": ",".join(sorted(evidence)),
        },
    }


def _synthesis_response(messages: list[ChatMessage]) -> str:
    evidence = _commander_evidence(messages)
    if evidence is not None:
        return json.dumps(_tool_grounded_report(messages, evidence))

    blob = "\n".join(message.content or "" for message in messages).lower()
    incident_match = re.search(r"\binc-[a-z0-9-]{8,}\b", blob)
    incident_id = incident_match.group(0) if incident_match else "inc-fixture001"

    if "postgres-primary" in blob or "postgres" in blob:
        service = "postgres-primary"
        category = "database"
        p_level = "P1"
        owner_team = "Database Reliability"
        escalation_path = [
            "Primary Database Reliability On-Call",
            "Secondary Database Reliability On-Call",
        ]
        citation = {
            "source_id": "database_connectivity",
            "source_type": "runbook",
            "quote": "Check connection pool saturation, lock waits, and recent migrations.",
        }
    elif "redis-cache" in blob or "k8s-ingress" in blob:
        service = "redis-cache" if "redis-cache" in blob else "k8s-ingress"
        category = "infra"
        p_level = "P2"
        owner_team = "Infra SRE"
        escalation_path = [
            "Primary Infra SRE On-Call",
            "Secondary Infra SRE On-Call",
        ]
        citation = {
            "source_id": (
                "redis_cache_degradation" if service == "redis-cache" else "ingress_5xx"
            ),
            "source_type": "runbook",
            "quote": "Inspect the affected infrastructure metrics and recent changes.",
        }
    else:
        service = "shop-web" if "shop-web" in blob else "orders-api"
        category = "application"
        p_level = "P3"
        owner_team = "App Platform"
        escalation_path = [
            "Primary App Platform On-Call",
            "Secondary App Platform On-Call",
        ]
        citation = {
            "source_id": (
                "shop_web" if service == "shop-web" else "orders_api_error_spike"
            ),
            "source_type": "service_doc" if service == "shop-web" else "runbook",
            "quote": "Check customer impact, recent deploys, and downstream dependencies.",
        }

    return json.dumps(
        {
            "incident_id": incident_id,
            "category": category,
            "p_level": p_level,
            "summary": f"Fixture synthesis: {service} requires evidence-based triage.",
            "probable_cause": "Recent-change correlation requires verification.",
            "citations": [citation],
            "owner_team": owner_team,
            "escalation_path": escalation_path,
            "recommended_steps": [
                f"Review recent changes and health metrics for {service}.",
                "Compare current signals against the documented baseline.",
            ],
            "confidence": 0.82,
            "guardrail_flags": [],
            "generated_at": "2026-07-10T12:05:00Z",
            "model_meta": {"provider": "fixture", "model": "peter-stage-a-fixture"},
        }
    )


def _parse_tool_result(message: ChatMessage) -> dict[str, Any]:
    try:
        parsed = json.loads(message.content or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "raw": message.content or ""}
    if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
        return parsed[0]
    return parsed if isinstance(parsed, dict) else {"value": parsed}


def _tool_message_name(messages: list[ChatMessage], message: ChatMessage) -> str:
    if message.name:
        return message.name
    for previous in reversed(messages):
        for tool_call in previous.tool_calls or []:
            if tool_call.get("id") == message.tool_call_id:
                return str(tool_call.get("function", {}).get("name", ""))
    return ""


def _agent_sequence(messages: list[ChatMessage]) -> list[str]:
    incident_text = "\n".join(
        message.content or "" for message in messages if message.role == "user"
    ).lower()
    complex_incident = any(
        marker in incident_text
        for marker in ("cross-domain", "redis-cache", "k8s-ingress")
    )
    if complex_incident:
        return ["Predictor_Tool", "LangGraph_Agent_Tool"]
    return ["Predictor_Tool", "RAG_Query_Tool", "Service_Context_Tool"]


def _next_agent_tool(
    messages: list[ChatMessage],
    available_tools: list[str | None],
) -> tuple[str, dict[str, Any]] | None:
    completed = [message for message in messages if message.role == "tool"]
    sequence = [
        tool_name
        for tool_name in _agent_sequence(messages)
        if tool_name in available_tools
    ]
    if len(completed) >= len(sequence):
        return None

    tool_name = sequence[len(completed)]
    incident_text = next(
        (message.content or "" for message in reversed(messages) if message.role == "user"),
        "triage this incident",
    )
    if tool_name == "RAG_Query_Tool":
        arguments = {"query": incident_text[:500]}
    elif tool_name == "LangGraph_Agent_Tool":
        arguments = {"question": incident_text[:500]}
    elif tool_name == "Service_Context_Tool":
        predictor = _parse_tool_result(completed[0]) if completed else {}
        severity = int(predictor.get("severity", 3))
        p_level = {5: "P1", 4: "P2", 3: "P3", 2: "P4", 1: "P4"}.get(
            severity, "P3"
        )
        arguments = {"severity": p_level}
    else:
        arguments = {}
    return tool_name, arguments


def _agent_evidence(messages: list[ChatMessage]) -> str:
    keys = {
        "Predictor_Tool": "predictor",
        "RAG_Query_Tool": "rag",
        "Service_Context_Tool": "service_context",
        "LangGraph_Agent_Tool": "langgraph",
    }
    evidence: dict[str, Any] = {}
    for message in messages:
        tool_name = _tool_message_name(messages, message)
        if message.role == "tool" and tool_name in keys:
            evidence[keys[tool_name]] = _parse_tool_result(message)
    return json.dumps(evidence)


def _response_for_task(task: TaskKind, messages: list[ChatMessage]) -> str:
    if task == "extract":
        return _extract_response(messages)
    if task == "synthesis":
        return _synthesis_response(messages)
    if task == "assistant":
        return (
            "I can help with incident triage for shop-web, orders-api, and postgres-primary. "
            "I will not invent SLAs or destructive commands."
        )
    if task == "rag_generate":
        return "Retrieved runbook guidance indicates checking deploy correlation and connection pools."
    return "Use RAG, Predictor, and LangGraph tools to investigate before synthesising the TriageReport."


def _require_token(authorization: str | None) -> None:
    expected = os.environ.get("PETER_SERVICES_TOKEN", "").strip()
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    provided = authorization.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="invalid bearer token")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/readyz")
async def readyz() -> dict[str, bool]:
    return {"ready": True}


@app.get("/v1/models")
async def list_models(
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """OpenAI-compatible model list — n8n lmChatOpenAi probes this on connect."""
    _require_token(authorization)
    return {
        "object": "list",
        "data": [
            {
                "id": "peter-stage-a-fixture",
                "object": "model",
                "created": 0,
                "owned_by": "peter-pan",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    payload: ChatCompletionRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    _require_token(authorization)
    task = _detect_task(payload.messages)
    fixture_id = _fixture_id(payload.messages)
    tool_names = [
        tool.get("function", {}).get("name")
        for tool in payload.tools
        if tool.get("type") == "function"
    ]
    if "format_final_json_response" in tool_names:
        task = "synthesis"
    agent_tool = (
        _next_agent_tool(payload.messages, tool_names)
        if task == "agent" and tool_names
        else None
    )
    if task == "agent" and any(
        message.role == "tool" for message in payload.messages
    ):
        content = _agent_evidence(payload.messages)
    else:
        content = _response_for_task(task, payload.messages)
    requires_codeblock = any(
        "include the enclosing markdown codeblock" in (message.content or "").lower()
        for message in payload.messages
    )
    if task == "synthesis" and requires_codeblock:
        content = f"```json\n{content}\n```"
    logger.info(
        json.dumps(
            {
                "event": "fixture_response",
                "api": "chat_completions",
                "task": task,
                "fixture_id": fixture_id,
                "tool_names": tool_names,
                "response_format": (
                    payload.response_format.get("type")
                    if payload.response_format
                    else None
                ),
                "stream": payload.stream,
                "next_tool": agent_tool[0] if agent_tool else None,
            }
        )
    )
    structured_tool = (
        "format_final_json_response"
        if "format_final_json_response" in tool_names
        else None
    )
    if agent_tool:
        tool_name, arguments = agent_tool
        message = {
            "role": "assistant",
            "content": None,
            "refusal": None,
            "tool_calls": [
                {
                    "id": f"call_{fixture_id.removeprefix('fix-')}",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(arguments),
                    },
                }
            ],
        }
        finish_reason = "tool_calls"
    elif structured_tool:
        message: dict[str, Any] = {
            "role": "assistant",
            "content": None,
            "refusal": None,
            "tool_calls": [
                {
                    "id": f"call_{fixture_id.removeprefix('fix-')}",
                    "type": "function",
                    "function": {
                        "name": structured_tool,
                        "arguments": content,
                    },
                }
            ],
        }
        finish_reason = "tool_calls"
    else:
        message = {"role": "assistant", "content": content}
        if payload.response_format and payload.response_format.get("type") in {
            "json_object",
            "json_schema",
        }:
            message["parsed"] = json.loads(content)
        finish_reason = "stop"
    return {
        "id": f"chatcmpl-{fixture_id}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": payload.model,
        "choices": [
            {
                "index": 0,
                "message": message,
                "logprobs": None,
                "finish_reason": finish_reason,
            }
        ],
        "system_fingerprint": None,
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "peter_meta": {"task": task, "fixture_id": fixture_id},
    }


@app.post("/v1/responses")
async def responses(
    payload: ResponsesRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    _require_token(authorization)
    messages = _responses_messages(payload)
    task = _detect_task(messages)
    fixture_id = _fixture_id(messages)
    logger.info(
        json.dumps(
            {
                "event": "fixture_response",
                "api": "responses",
                "task": task,
                "fixture_id": fixture_id,
                "message_roles": [message.role for message in messages],
            }
        )
    )
    content = _response_for_task(task, messages)
    return {
        "id": f"resp-{fixture_id}",
        "object": "response",
        "created_at": int(time.time()),
        "status": "completed",
        "error": None,
        "incomplete_details": None,
        "model": payload.model,
        "output": [
            {
                "id": f"msg-{fixture_id}",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "text": content,
                    }
                ],
            }
        ],
        "parallel_tool_calls": False,
        "tool_choice": "auto",
        "tools": [],
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        },
        "peter_meta": {"task": task, "fixture_id": fixture_id},
    }
