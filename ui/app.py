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
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import streamlit as st

from lib import (
    OFF_TOPIC_REPLY,
    SYSTEM_PROMPT,
    Signal,
    SubmissionResult,
    check_health,
    chat_sync,
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

# ---------------------------------------------------------------------------
# Sidebar: service health
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🪝 PETER PAN")
    st.caption("Layer 1 — Incident Response WebUI")
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
        "🟢 webhook configured" if _webhook_ok else "⚠️ PETER_UI_N8N_WEBHOOK_URL not set"
    )

    if st.button("↺ Refresh health", use_container_width=True, key="refresh_health"):
        st.rerun()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_assistant, tab_submit = st.tabs(["💬 Assistant", "📋 Incident Submission"])

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
                with st.spinner("Thinking…"):
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
                    except RuntimeError as exc:
                        _reply = f"⚠️ LLM unavailable: {exc}"
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
                placeholder="High error rate on checkout service",
            )
            _body_input = st.text_area(
                "Description",
                max_chars=8000,
                height=150,
                placeholder="Symptoms, timeline, initial impact…",
            )

            _svc_input = st.text_input("Service slug", placeholder="checkout-api")
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
                _label_val = st.text_input("Label value", placeholder="platform")

            _form_submitted = st.form_submit_button(
                "Submit Signal →",
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
                )

                _result: SubmissionResult = submit_signal(
                    _signal, _N8N_WEBHOOK_URL, _WEBHOOK_SECRET
                )

                if _result.ok:
                    st.success(
                        f"Signal `{_signal.id}` submitted (HTTP {_result.status_code})"
                    )
                    st.json(_signal.model_dump(mode="json"))
                elif _result.status_code == 0:
                    st.warning(
                        f"⚠️ Webhook unreachable — signal NOT forwarded.\n\n{_result.detail}"
                    )
                    st.info("Signal JSON (retain for manual retry):")
                    st.json(_signal.model_dump(mode="json"))
                else:
                    st.error(
                        f"Submission failed (HTTP {_result.status_code}): {_result.detail}"
                    )

    with _col_info:
        st.subheader("Signal Contract")
        st.caption("webui → n8n (Signal JSON)")
        st.code(
            'source: "webui"\nkind:   "manual"\nid:     sig-<12-hex>\nreceived_at: ISO-8601 UTC\ntitle:  1–300 chars\nbody:   0–8000 chars\nservice: slug | null\nenvironment: str | null\nseverity_hint: critical|warning|info|null',
            language="yaml",
        )

    # ---- Review Queue ------------------------------------------------
    st.divider()
    st.subheader("🔍 Review Queue")
    st.caption(
        "TriageReports with non-empty ``guardrail_flags`` — "
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
                    st.json(_report)
                with _ac:
                    if st.button(
                        "✓ Dismiss",
                        key=f"dismiss_{_idx}_{_inc_id}",
                        help="Remove from review queue",
                    ):
                        st.session_state["review_queue"].pop(_idx)
                        st.rerun()
    else:
        st.info("Review queue is empty.")

    if st.button(
        "➕ Inject test report (dev)",
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
            "owner_team": "platform",
            "escalation_path": ["on-call-sre", "platform-lead"],
            "recommended_steps": [
                "Check /metrics for pool exhaustion",
                "Review pool config",
                "Initiate rollback if degradation > 5 min",
            ],
            "confidence": 0.72,
            "guardrail_flags": ["low_confidence", "missing_deploy_context"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_meta": {"provider": "fixture", "model_id": "fixture-v1"},
        }
        st.session_state["review_queue"].append(_dummy)
        st.rerun()
