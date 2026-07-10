"""LangGraph Agent Service — ``POST /agent/run`` (BUILD_PLAN §3, LangGraph
agent row).

Thin FastAPI wrapper around the ``graph.run`` pipeline (see ``graph.py`` for
the actual Planner -> Specialists -> Synthesiser logic and the Stage A
limitations). The synthesised report is always validated against the
vendored ``TriageReport`` contract before it leaves this service — on
validation failure we return 500 rather than ever emit an invalid report.
"""

from __future__ import annotations

import os

import httpx
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, ValidationError

from .auth import require_bearer_token
from .contracts import TriageReport
from .graph import run as run_graph

SERVICE_NAME = "langgraph-agent"

app = FastAPI(title="PETER PAN LangGraph Agent Service")

_CLIENT_TIMEOUT_SECONDS = 3.0


class AgentRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    incident: dict
    question: str | None = None


def _build_client() -> httpx.AsyncClient:
    """Factory so tests can monkeypatch in an ``httpx.MockTransport`` client
    without touching real network I/O."""
    return httpx.AsyncClient(timeout=_CLIENT_TIMEOUT_SECONDS)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "service": SERVICE_NAME}


@app.post("/agent/run", dependencies=[Depends(require_bearer_token)])
async def agent_run(payload: AgentRunRequest) -> dict:
    rag_url = os.environ.get("PETER_RAG_URL", "")
    tools_url = os.environ.get("PETER_TOOLS_URL", "")

    async with _build_client() as client:
        report_dict = await run_graph(
            payload.incident,
            payload.question,
            rag_url=rag_url,
            tools_url=tools_url,
            client=client,
        )

    try:
        report = TriageReport.model_validate(report_dict)
    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"synthesised report failed TriageReport contract validation: {exc}",
        ) from exc

    return report.model_dump(mode="json")
