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
    content: str


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
    blob = "\n".join(m.content for m in messages).lower()
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
    user = next((m.content for m in reversed(messages) if m.role == "user"), "")
    service = "orders-api"
    normalized = user.lower()
    known_services = {
        "postgres-primary": ("postgres-primary", "postgres"),
        "shop-web": ("shop-web",),
        "orders-api": ("orders-api",),
        "payments-api": ("payments-api",),
        "redis-cache": ("redis-cache", "redis"),
        "k8s-ingress": ("k8s-ingress", "ingress"),
    }
    for canonical, aliases in known_services.items():
        if any(alias in normalized for alias in aliases):
            service = canonical
            break
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


def _synthesis_response(messages: list[ChatMessage]) -> str:
    blob = "\n".join(message.content for message in messages).lower()
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
    content = _response_for_task(task, payload.messages)
    requires_codeblock = any(
        "include the enclosing markdown codeblock" in message.content.lower()
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
            }
        )
    )
    structured_tool = (
        "format_final_json_response"
        if "format_final_json_response" in tool_names
        else None
    )
    if structured_tool:
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
