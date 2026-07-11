"""PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1).

Canonical copy. Each service vendors an identical copy as ``<pkg>/contracts.py``;
a contract test asserts the copies match this file byte-for-byte. Changing anything
here requires an ADR.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Signal(BaseModel):
    """Anything that enters the system: Grafana alert, WebUI form, deploy event, complaint."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^sig-[a-z0-9-]{8,}$")
    source: Literal["grafana", "webui", "github", "slack"]
    kind: Literal["alert", "manual", "deploy_event", "complaint"]
    received_at: datetime
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(default="", max_length=8000)
    service: str | None = None          # normalized service slug when known
    environment: str | None = None      # e.g. "production" | "staging"
    severity_hint: Literal["critical", "warning", "info"] | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)  # original payload, never interpreted downstream


class DeployRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repo: str
    sha: str
    deployed_at: datetime
    service: str


class IncidentContext(BaseModel):
    """Output of the n8n context-enrichment branches (nodes MW/DEP/CMP → merge)."""
    model_config = ConfigDict(extra="forbid")
    maintenance_window: bool = False
    recent_deploys: list[DeployRef] = Field(default_factory=list)
    complaint_count: int = 0
    complaint_samples: list[str] = Field(default_factory=list, max_length=5)


class Incident(BaseModel):
    """A draft or confirmed incident flowing through n8n into the agent."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^inc-[a-z0-9-]{8,}$")
    created_at: datetime
    status: Literal["draft", "triaging", "suppressed", "rejected", "triaged", "review"]
    signal_ids: list[str] = Field(min_length=1)
    service: str
    environment: str
    p_level: Literal["P1", "P2", "P3", "P4"] | None = None  # None until triage assigns it
    started_at: datetime | None = None
    symptom: str = Field(min_length=1, max_length=1000)
    context: IncidentContext = Field(default_factory=IncidentContext)


class GuardrailResult(BaseModel):
    """Frozen response returned by both Guardrails checks."""
    model_config = ConfigDict(extra="forbid")

    passed: bool
    flags: list[str] = Field(default_factory=list)
    reason: str = Field(default="", max_length=500)


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str            # corpus doc id or tool call id
    source_type: Literal["runbook", "incident_history", "service_doc", "tool_result"]
    quote: str = Field(max_length=500)


class TriageReport(BaseModel):
    """The one artifact PETER PAN produces. Output-guardrail-checked before routing."""
    model_config = ConfigDict(extra="forbid")

    incident_id: str
    category: Literal["infra", "database", "application"]   # drives n8n router node 8
    p_level: Literal["P1", "P2", "P3", "P4"]
    summary: str = Field(min_length=1, max_length=1200)
    probable_cause: str = Field(max_length=1200)
    citations: list[Citation] = Field(min_length=1)          # cited answers only — uncited = guardrail fail
    owner_team: str
    escalation_path: list[str] = Field(default_factory=list) # ordered roles, from Tools API only
    recommended_steps: list[str] = Field(default_factory=list, max_length=8)  # read-only/safe steps only
    confidence: float = Field(ge=0.0, le=1.0)
    guardrail_flags: list[str] = Field(default_factory=list) # non-empty → human review queue
    generated_at: datetime
    model_meta: dict[str, str] = Field(default_factory=dict) # provider, model id, fixture id in Stage A
