"""PETER PAN Layer 1 — Streamlit WebUI.

Two tabs:
  - Assistant: grounded SRE chat via fixture LLM / Ollama adapter.
  - Incident Submission: Signal form → n8n webhook + TriageReport review queue.

Env vars consumed (all optional with safe defaults):
  PETER_UI_N8N_WEBHOOK_URL   n8n webhook for Signal submission
  PETER_WEBHOOK_SECRET       X-Peter-Webhook-Secret header value
  PETER_FIXTURE_LLM_URL      OpenAI-compatible fixture LLM base URL
  PETER_OLLAMA_URL            Ollama base URL (fallback)
  PETER_OLLAMA_MODEL          Ollama model name (default: llama3)
  PETER_INGESTION_URL         Ingestion service base URL (health check)
  PETER_RAG_URL               RAG service base URL (health check)
  PETER_GUARDRAILS_URL        Guardrails service base URL (health check)
  PETER_TOOLS_URL             Tools API base URL (health check)
  PETER_LLM_PROVIDER          fixture | ollama | … (badge only)
  GRAFANA_URL                 optional dashboard deep-link base
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import streamlit as st

from lib import (
    OFF_TOPIC_REPLY,
    SYSTEM_PROMPT,
    Signal,
    SubmissionResult,
    check_health,
    chat_sync,
    extract_triage_report,
    health_url,
    is_off_topic,
    new_sig_id,
    submit_signal,
)

# ---------------------------------------------------------------------------
# Config from environment
# ---------------------------------------------------------------------------

_N8N_WEBHOOK_URL: str = os.environ.get("PETER_UI_N8N_WEBHOOK_URL", "")
_WEBHOOK_SECRET: str = os.environ.get("PETER_WEBHOOK_SECRET", "")
_FIXTURE_LLM_URL: str = os.environ.get("PETER_FIXTURE_LLM_URL", "")
_OLLAMA_URL: str = os.environ.get("PETER_OLLAMA_URL", "")
_OLLAMA_MODEL: str = os.environ.get("PETER_OLLAMA_MODEL", "llama3")
_LLM_PROVIDER: str = os.environ.get("PETER_LLM_PROVIDER", "fixture").strip().lower()
_GRAFANA_URL: str = os.environ.get("GRAFANA_URL", "").rstrip("/")

_HEALTH_ENDPOINTS: dict[str, str] = {
    "ingestion": health_url(os.environ.get("PETER_INGESTION_URL", "")),
    "rag": health_url(os.environ.get("PETER_RAG_URL", "")),
    "guardrails": health_url(os.environ.get("PETER_GUARDRAILS_URL", "")),
    "tools-api": health_url(os.environ.get("PETER_TOOLS_URL", "")),
    "fixture-llm": health_url(
        _FIXTURE_LLM_URL.removesuffix("/v1") if _FIXTURE_LLM_URL else ""
    ),
}

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="PETER PAN",
    page_icon="🪝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state["messages"]: list[dict[str, str]] = []
if "review_queue" not in st.session_state:
    st.session_state["review_queue"]: list[dict] = []
if "last_submission" not in st.session_state:
    st.session_state["last_submission"]: dict[str, Any] | None = None


def _render_triage_report(report: dict[str, Any]) -> None:
    """Structured TriageReport blocks (metrics + citations + steps)."""
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Category", str(report.get("category") or "—"))
    m2.metric("Severity", str(report.get("p_level") or "—"))
    m3.metric("Owner", str(report.get("owner_team") or "—"))
    conf = report.get("confidence")
    m4.metric(
        "Confidence",
        f"{float(conf):.0%}" if isinstance(conf, (int, float)) else "—",
    )

    st.markdown("**Summary**")
    st.write(report.get("summary") or "—")
    st.markdown("**Probable cause**")
    st.write(report.get("probable_cause") or "—")

    citations = report.get("citations") or []
    if citations:
        with st.expander(f"Citations ({len(citations)})", expanded=True):
            for cite in citations:
                if not isinstance(cite, dict):
                    continue
                st.markdown(
                    f"- `{cite.get('source_id', '?')}` "
                    f"({cite.get('source_type', '?')}): "
                    f"{cite.get('quote', '')}"
                )

    steps = report.get("recommended_steps") or []
    if steps:
        st.markdown("**Recommended steps**")
        for step in steps:
            st.markdown(f"- {step}")

    flags = report.get("guardrail_flags") or []
    if flags:
        st.warning("Guardrail flags: " + ", ".join(str(f) for f in flags))

    if _GRAFANA_URL:
        st.link_button("Open Grafana", _GRAFANA_URL, use_container_width=False)

    with st.expander("Raw response", expanded=False):
        st.json(report)


def _render_guardrail_card(payload: dict[str, Any], title: str) -> None:
    st.error(title)
    c1, c2 = st.columns(2)
    c1.write(f"**passed:** `{payload.get('passed')}`")
    c2.write(f"**status:** `{payload.get('status', '—')}`")
    flags = payload.get("flags") or []
    st.write("**flags:** " + (", ".join(str(f) for f in flags) if flags else "—"))
    st.write("**reason:** " + str(payload.get("reason") or "—"))
    with st.expander("Raw response", expanded=False):
        st.json(payload)


def _handle_submission(result: SubmissionResult, signal: Signal) -> None:
    """Render webhook outcome and update review queue when flagged."""
    st.session_state["last_submission"] = {
        "kind": result.kind,
        "status_code": result.status_code,
        "signal_id": signal.id,
    }
    body = result.body if isinstance(result.body, dict) else {}

    if result.kind == "triage_report":
        report = extract_triage_report(body) or body
        st.success(
            f"Triage complete for `{signal.id}` (HTTP {result.status_code})"
        )
        _render_triage_report(report)
        return

    if result.kind == "rejected":
        _render_guardrail_card(body or {"reason": result.detail}, "Signal rejected")
        return

    if result.kind == "flagged_for_review":
        report = extract_triage_report(body) or body.get("report") or body
        if isinstance(report, dict):
            st.session_state["review_queue"].insert(0, report)
        st.warning(
            f"Flagged for human review (HTTP {result.status_code}). "
            "See Review Queue below."
        )
        if isinstance(report, dict) and (
            "incident_id" in report or "summary" in report
        ):
            _render_triage_report(report)
        else:
            _render_guardrail_card(
                body or {"reason": result.detail}, "Flagged for review"
            )
        return

    if result.kind == "suppressed":
        st.info(
            f"Signal suppressed: {body.get('reason') or result.detail or 'known noise'}"
        )
        with st.expander("Raw response", expanded=False):
            st.json(body or {"detail": result.detail})
        return

    if result.kind == "predictor_invalid":
        st.error(
            body.get("reason")
            or result.detail
            or "Predictor returned an invalid classification."
        )
        with st.expander("Raw response", expanded=False):
            st.json(body or {"detail": result.detail})
        return

    if result.kind == "unreachable":
        st.warning(
            f"Webhook unreachable — signal NOT forwarded.\n\n{result.detail}"
        )
        st.info("Signal JSON (retain for manual retry):")
        st.json(signal.model_dump(mode="json"))
        return

    if result.kind == "misconfigured":
        st.error(result.detail or "Webhook URL not configured")
        return

    st.error(f"Submission failed (HTTP {result.status_code}): {result.detail}")
    if body:
        with st.expander("Raw response", expanded=False):
            st.json(body)


# ---------------------------------------------------------------------------
# Sidebar: service health
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("PETER PAN")
    st.caption("Layer 1 — Incident Response WebUI")
    if _LLM_PROVIDER in {"", "fixture"}:
        st.caption("demo data · fixture LLM")
    else:
        st.caption(f"LLM provider: `{_LLM_PROVIDER}`")
    st.divider()
    st.subheader("Service Health")

    _STATUS_ICON = {"ok": "🟢", "degraded": "🟡", "down": "🔴", "unknown": "⚪"}
    for _svc, _url in _HEALTH_ENDPOINTS.items():
        _status, _detail = check_health(_url)
        _icon = _STATUS_ICON.get(_status, "⚪")
        st.caption(f"{_icon} **{_svc}** — {_detail}")

    st.divider()
    _webhook_ok = bool(_N8N_WEBHOOK_URL)
    st.caption(
        "webhook configured" if _webhook_ok else "PETER_UI_N8N_WEBHOOK_URL not set"
    )

    if st.button("Refresh health", use_container_width=True, key="refresh_health"):
        st.rerun()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_assistant, tab_submit = st.tabs(["Assistant", "Incident Submission"])

# ============================================================
# Tab 1: SRE Assistant
# ============================================================

with tab_assistant:
    st.header("SRE Assistant")
    st.caption(
        "Grounded incident-response chat. "
        "Answers cite evidence — never invented SLAs, commands, or runbook steps."
    )

    for _msg in st.session_state["messages"]:
        with st.chat_message(_msg["role"]):
            st.markdown(_msg["content"])

    if _prompt := st.chat_input("Ask about an incident, service, or runbook…"):
        st.session_state["messages"].append({"role": "user", "content": _prompt})
        with st.chat_message("user"):
            st.markdown(_prompt)

        with st.chat_message("assistant"):
            if is_off_topic(_prompt):
                _reply = OFF_TOPIC_REPLY
                st.markdown(_reply)
            else:
                with st.status("Consulting fixture LLM…", expanded=False) as _status:
                    _msgs_to_send = [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *st.session_state["messages"],
                    ]
                    try:
                        _reply = chat_sync(
                            _msgs_to_send,
                            fixture_url=_FIXTURE_LLM_URL,
                            ollama_url=_OLLAMA_URL,
                            ollama_model=_OLLAMA_MODEL,
                        )
                        _status.update(label="Reply ready", state="complete")
                    except RuntimeError as exc:
                        _reply = f"LLM unavailable: {exc}"
                        _status.update(label="LLM unavailable", state="error")
                st.markdown(_reply)

        st.session_state["messages"].append({"role": "assistant", "content": _reply})

    if st.session_state["messages"]:
        if st.button("Clear conversation", key="clear_chat"):
            st.session_state["messages"] = []
            st.rerun()

# ============================================================
# Tab 2: Incident Submission
# ============================================================

with tab_submit:
    st.header("Incident Submission")
    st.caption("Submit a manual signal directly to the n8n orchestration pipeline.")

    _col_form, _col_info = st.columns([2, 1])

    with _col_form:
        with st.form("incident_form", clear_on_submit=False):
            _title_input = st.text_input(
                "Title *",
                max_chars=300,
                placeholder="orders-api HTTP 5xx surge after deploy",
            )
            _body_input = st.text_area(
                "Description",
                max_chars=8000,
                height=150,
                placeholder="Symptoms, timeline, initial impact…",
            )

            _svc_input = st.text_input(
                "Service slug",
                placeholder="orders-api",
                help="Use a catalog service: orders-api, postgres-primary, shop-web, …",
            )
            _env_input = st.selectbox(
                "Environment", ["", "production", "staging", "development"]
            )
            _sev_input = st.selectbox(
                "Severity hint", ["", "critical", "warning", "info"]
            )

            st.caption("Optional label (single key / value)")
            _lk_col, _lv_col = st.columns(2)
            with _lk_col:
                _label_key = st.text_input("Label key", placeholder="team")
            with _lv_col:
                _label_val = st.text_input("Label value", placeholder="checkout")

            _form_submitted = st.form_submit_button(
                "Submit Signal",
                use_container_width=True,
                type="primary",
            )

        if _form_submitted:
            if not _title_input.strip():
                st.error("Title is required.")
            else:
                _labels: dict[str, str] = {}
                if _label_key.strip() and _label_val.strip():
                    _labels[_label_key.strip()] = _label_val.strip()

                _signal = Signal(
                    id=new_sig_id(),
                    source="webui",
                    kind="manual",
                    received_at=datetime.now(timezone.utc),
                    title=_title_input.strip(),
                    body=_body_input.strip(),
                    service=_svc_input.strip() or None,
                    environment=_env_input or None,
                    severity_hint=_sev_input or None,
                    labels=_labels,
                    raw={"metric_window_ref": "spike"},
                )

                with st.status(
                    "Submitting to n8n — enriching, classifying, writing brief…",
                    expanded=True,
                ) as _sub_status:
                    _result: SubmissionResult = submit_signal(
                        _signal, _N8N_WEBHOOK_URL, _WEBHOOK_SECRET
                    )
                    _sub_status.update(
                        label=f"Done (HTTP {_result.status_code or 0})",
                        state="complete" if _result.ok else "error",
                    )

                _handle_submission(_result, _signal)

    with _col_info:
        st.subheader("Signal Contract")
        st.caption("webui → n8n (Signal JSON)")
        st.code(
            'source: "webui"\nkind:   "manual"\nid:     sig-<12-hex>\n'
            "received_at: ISO-8601 UTC\ntitle:  1–300 chars\n"
            "body:   0–8000 chars\nservice: catalog slug | null\n"
            "environment: str | null\n"
            "severity_hint: critical|warning|info|null",
            language="yaml",
        )

    # ---- Review Queue ------------------------------------------------
    st.divider()
    st.subheader("Review Queue")
    st.caption(
        "TriageReports flagged by output guardrails — "
        "requires human review before routing."
    )

    _queue = st.session_state["review_queue"]

    if _queue:
        for _idx, _report in enumerate(_queue):
            _flags = _report.get("guardrail_flags", [])
            _p = _report.get("p_level", "?")
            _inc_id = _report.get("incident_id", "unknown")
            _flag_label = ", ".join(_flags) if _flags else "none"

            with st.expander(
                f"[{_p}] {_inc_id} — flags: {_flag_label}",
                expanded=(_idx == 0),
            ):
                _rc, _ac = st.columns([3, 1])
                with _rc:
                    _render_triage_report(_report)
                with _ac:
                    if st.button(
                        "Dismiss",
                        key=f"dismiss_{_idx}_{_inc_id}",
                        help="Remove from review queue",
                    ):
                        st.session_state["review_queue"].pop(_idx)
                        st.rerun()
    else:
        st.info("Review queue is empty.")

    if st.button(
        "Inject test report (dev)",
        key="inject_report",
        help="Insert a mock flagged TriageReport for UI testing",
    ):
        _dummy: dict = {
            "incident_id": "inc-demo0001",
            "category": "application",
            "p_level": "P2",
            "summary": (
                "Elevated 5xx on checkout — possible DB connection-pool exhaustion."
            ),
            "probable_cause": "Pool saturation following deploy v1.3.2.",
            "citations": [
                {
                    "source_id": "runbook-checkout-002",
                    "source_type": "runbook",
                    "quote": "Check pool size via /metrics endpoint.",
                }
            ],
            "owner_team": "App Platform",
            "escalation_path": ["on-call-sre", "platform-lead"],
            "recommended_steps": [
                "Check /metrics for pool exhaustion",
                "Review pool config",
                "Initiate rollback if degradation exceeds change window",
            ],
            "confidence": 0.72,
            "guardrail_flags": ["low_confidence", "missing_deploy_context"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_meta": {"provider": "fixture", "model_id": "fixture-v1"},
        }
        st.session_state["review_queue"].append(_dummy)
        st.rerun()
