"""Preview-first escalation service.

Builds a read-only escalation preview from ``escalation_policies.json`` +
``service_owners.csv`` and appends an audit record to SQLite. This service
**never** dispatches externally — ``notification_dispatch.py`` holds the
Stage C live-dispatch primitives but nothing here calls them.

Replaces the legacy ``escalation_lambda.py``, which invoked a local AWS-Lambda
handler under the deleted ``action_groups/`` path through the now-deleted
``lambda_root`` bootstrap. The same preview/mask/notify logic now lives here
as plain, directly testable functions — no Lambda, no event/response envelope.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools_api import data_access
from tools_api.contracts import TriageReport
from tools_api.escalation_message import (
    enrich_escalation_context,
    format_escalation_messages,
)
from tools_api.incident_analysis import _find_service_owner, _resolve_escalation


class EscalationServiceError(RuntimeError):
    """Raised when an escalation preview cannot be built (e.g. unknown team)."""


def mask_recipient(recipient: str) -> str:
    """Mask a raw recipient (email/phone) for safe logging and audit display."""
    if not recipient:
        return ""
    if len(recipient) <= 4:
        return "*" * len(recipient)
    return f"{recipient[:2]}***{recipient[-2:]}"


def _first_env(*names: str) -> str:
    """Return the first non-empty environment value among names."""
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def resolve_demo_recipients(channel: str) -> list[str]:
    """Resolve all escalation recipients for a channel from environment variables ONLY.

    Values may be comma/semicolon-separated to support multi-recipient escalation
    (e.g. ``PETER_ESCALATION_EMAIL="a@x.com,b@y.com"``). Recipients are never
    read from git or request bodies. Unused while dispatch stays preview-only,
    kept for the Stage C live-dispatch wire-up.
    """
    channel = channel.strip().lower()
    if channel == "sms":
        raw = _first_env("PETER_ESCALATION_SMS", "PETER_DEMO_SMS_RECIPIENT")
    elif channel == "whatsapp":
        raw = _first_env(
            "PETER_ESCALATION_SMS",
            "PETER_DEMO_WHATSAPP_RECIPIENT",
            "PETER_DEMO_SMS_RECIPIENT",
        )
    elif channel == "email":
        raw = _first_env("PETER_ESCALATION_EMAIL", "PETER_DEMO_EMAIL_RECIPIENT")
    else:
        raise ValueError(f"Unknown channel: {channel}")
    seen: set[str] = set()
    recipients: list[str] = []
    for part in raw.replace(";", ",").split(","):
        value = part.strip()
        if value and value.lower() not in seen:
            seen.add(value.lower())
            recipients.append(value)
    return recipients


def resolve_demo_recipient(channel: str) -> str:
    """Resolve the primary escalation recipient (first configured) for a channel."""
    recipients = resolve_demo_recipients(channel)
    return recipients[0] if recipients else ""


def _find_owner_by_team_or_service(
    identifier: str, source_dir: Path | None
) -> dict[str, Any] | None:
    """Find a service_owners row by exact service slug, else by owning team name.

    ``TriageReport.owner_team`` is a team name (e.g. "App Platform"), not a
    service slug; several services can share a team, but this dataset's
    on-call roles are defined per team, so any matching row yields the same
    escalation roles.
    """
    owner = _find_service_owner(identifier, source_dir)
    if owner:
        return owner
    needle = identifier.strip().lower()
    for row in data_access.load_service_owners(source_dir):
        if row["owning_team"].strip().lower() == needle:
            return _find_service_owner(row["service"], source_dir)
    return None


def build_escalation_preview(
    *,
    report: TriageReport,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Build a read-only escalation preview for a TriageReport. Never dispatches."""
    base = Path(data_dir) if data_dir else None
    owner = _find_owner_by_team_or_service(report.owner_team, base)
    if owner is None:
        raise EscalationServiceError(
            f"Unknown owning team or service '{report.owner_team}'"
        )

    escalation = _resolve_escalation(
        priority=report.p_level, owner=owner, source_dir=base
    )
    notify_path = report.escalation_path or escalation["notify"]

    ctx = enrich_escalation_context(
        {
            "environment": "production",
            "incident_title": report.summary,
            "owner_team": owner["owner_team"],
            "slack_channel": owner["slack_channel"],
            "on_call_name": owner["primary_on_call"],
            "recommended_actions": report.recommended_steps,
        },
        incident_id=report.incident_id,
        service=owner["service"],
        severity=report.p_level,
    )
    formatted = format_escalation_messages(ctx, channel="email")

    escalation_id = (
        f"ESC-{datetime.now(timezone.utc):%Y%m%d%H%M%S}-{uuid.uuid4().hex[:8]}"
    )
    return {
        "escalation_id": escalation_id,
        "preview": True,
        "message": formatted["body"],
        "escalation_path": notify_path,
        "service": owner["service"],
        "owner_team": owner["owner_team"],
        "p_level": report.p_level,
        "war_room_required": bool(escalation["war_room_required"]),
        "compliance_overrides": escalation["compliance_overrides"],
        "subject": formatted["subject"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


# --- Audit log (SQLite; append-only preview trail) -------------------------


def _audit_db_path(db_path: str | Path | None = None) -> Path:
    if db_path:
        return Path(db_path)
    override = os.environ.get("TOOLS_AUDIT_DB", "").strip()
    return Path(override) if override else Path("audit.sqlite")


@contextmanager
def _audit_connection(db_path: str | Path | None = None):
    path = _audit_db_path(db_path)
    if str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS escalation_audit (
                escalation_id TEXT PRIMARY KEY,
                incident_id TEXT,
                service TEXT,
                owner_team TEXT,
                p_level TEXT,
                preview_requested INTEGER,
                dispatched INTEGER,
                message TEXT,
                escalation_path TEXT,
                created_at TEXT
            )
            """)
        yield conn
        conn.commit()
    finally:
        conn.close()


def record_audit_entry(
    entry: dict[str, Any], *, db_path: str | Path | None = None
) -> None:
    """Append one escalation preview to the audit log. Never marks ``dispatched``."""
    with _audit_connection(db_path) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO escalation_audit
            (escalation_id, incident_id, service, owner_team, p_level, preview_requested,
             dispatched, message, escalation_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["escalation_id"],
                entry.get("incident_id", ""),
                entry.get("service", ""),
                entry.get("owner_team", ""),
                entry.get("p_level", ""),
                1 if entry.get("preview_requested", True) else 0,
                0,  # this service never dispatches externally
                entry.get("message", ""),
                json.dumps(entry.get("escalation_path", [])),
                entry.get("created_at") or datetime.now(timezone.utc).isoformat(),
            ),
        )


def list_audit_entries(
    limit: int = 50, *, db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    """Return the most recent audit entries, newest first."""
    with _audit_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM escalation_audit ORDER BY created_at DESC, rowid DESC LIMIT ?",
            (limit,),
        ).fetchall()
    entries: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["escalation_path"] = json.loads(item.get("escalation_path") or "[]")
        item["preview_requested"] = bool(item["preview_requested"])
        item["dispatched"] = bool(item["dispatched"])
        entries.append(item)
    return entries


def create_escalation(
    *,
    report: TriageReport,
    preview: bool = True,
    data_dir: Path | None = None,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build the preview and append the audit record in one call (route entry point)."""
    result = build_escalation_preview(report=report, data_dir=data_dir)
    record_audit_entry(
        {
            "escalation_id": result["escalation_id"],
            "incident_id": report.incident_id,
            "service": result["service"],
            "owner_team": result["owner_team"],
            "p_level": result["p_level"],
            "preview_requested": preview,
            "message": result["message"],
            "escalation_path": result["escalation_path"],
            "created_at": result["created_at"],
        },
        db_path=db_path,
    )
    return result
