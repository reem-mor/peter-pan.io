"""Harden PETER Stage A workflow via n8n REST API (Cloud or self-hosted).

Fixes:
- Guardrail IF: $json.pass -> $json.passed (frozen contract)
- Reject Signal: include passed:false
- Migrate deprecated langchain.httpRequestTool -> n8n-nodes-base.httpRequestTool
- Writer system message (messages path): P1-P4 only, no P5
- retryOnFail on guardrails + predictor/RAG/LangGraph tools
- Workflow description refresh

Does not print secrets. Uses N8N_API_KEY from env.
Workflow target from N8N_API_URL + N8N_WORKFLOW_ID (or name lookup).
Never hardcodes live account hostnames or workflow IDs.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

EXPORT_PATH = Path(__file__).resolve().parents[1] / "n8n" / "peter-flow.json"
DEFAULT_WORKFLOW_NAME = "PETER PAN — Observability Triage"

OLD_TOOL = "@n8n/n8n-nodes-langchain.httpRequestTool"
NEW_TOOL = "n8n-nodes-base.httpRequestTool"

WRITER_SYSTEM = (
    "You are the incident report writer. Synthesise the incident, the predictor "
    "severity/category, and the RAG runbook context into one TriageReport matching "
    "the schema exactly. Deterministic floors: category must be one of infra, "
    "database, application (derived from the predictor incident_class — never invent "
    "a fourth category). owner_team and escalation_path may ONLY be copied from tool "
    "results in the findings — if absent use \"unknown\" and []. p_level must be one "
    "of P1, P2, P3, P4 only — there is no P5; use the predictor proposal when present, "
    "otherwise map conservatively within P1–P4. Every citations[] entry must copy a "
    "real source_id, source_type and quote from tool output — never invent citations; "
    "if you cannot cite, say \"insufficient data\" in probable_cause and lower "
    "confidence. recommended_steps must be read-only or safe diagnostic actions, "
    "never destructive commands."
)

DESCRIPTION = (
    "Observability ingress: alert/webhook signal → input guardrails "
    "({passed,flags,reason}) → context enrichment → extractor → "
    "commander (predictor/RAG/service-context/langgraph) → deterministic 6→3 "
    "routing → output guardrails → team webhooks. Fixture-first Stage A."
)

REJECT_BODY = (
    "={{ { passed: false, status: 'rejected', "
    "reason: $json.reason ?? 'input failed guardrails', "
    "flags: $json.flags ?? [] } }}"
)


def api_base() -> str:
    raw = (os.environ.get("N8N_API_URL") or "").strip().rstrip("/")
    if not raw:
        raise SystemExit(
            "N8N_API_URL is required (e.g. https://<instance>/api/v1). "
            "Do not hardcode instance URLs in this script."
        )
    if raw.endswith("/api/v1"):
        return raw
    return f"{raw}/api/v1"


def api_key() -> str:
    key = os.environ.get("N8N_API_KEY") or ""
    if not key:
        raise SystemExit("N8N_API_KEY not in process env — run from a shell that has it")
    return key


def request(method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{api_base()}{path}",
        data=data,
        method=method,
        headers={
            "X-N8N-API-KEY": api_key(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code}: {err[:800]}") from e


def resolve_workflow_id() -> str:
    explicit = (os.environ.get("N8N_WORKFLOW_ID") or "").strip()
    if explicit:
        return explicit
    name = (os.environ.get("N8N_WORKFLOW_NAME") or DEFAULT_WORKFLOW_NAME).strip()
    listing = request("GET", "/workflows?limit=200")
    rows = listing.get("data") if isinstance(listing, dict) else listing
    if not isinstance(rows, list):
        raise SystemExit("unexpected /workflows response shape")
    matches = [
        w
        for w in rows
        if isinstance(w, dict)
        and w.get("name") == name
        and not w.get("isArchived")
    ]
    if not matches:
        raise SystemExit(
            f"no workflow named {name!r}; set N8N_WORKFLOW_ID or N8N_WORKFLOW_NAME"
        )
    if len(matches) > 1:
        ids = ", ".join(str(w.get("id")) for w in matches)
        raise SystemExit(f"multiple workflows named {name!r}: {ids}")
    return str(matches[0]["id"])


def fix_if_left_value(node: dict, field: str) -> bool:
    changed = False
    conditions = node.get("parameters", {}).get("conditions", {}).get("conditions")
    if not isinstance(conditions, list):
        return False
    for cond in conditions:
        lv = cond.get("leftValue", "")
        if isinstance(lv, str) and "$json.pass" in lv and "$json.passed" not in lv:
            cond["leftValue"] = lv.replace("$json.pass", f"$json.{field}")
            changed = True
    return changed


def ensure_retries(node: dict, max_tries: int = 3) -> bool:
    changed = False
    if not node.get("retryOnFail"):
        node["retryOnFail"] = True
        changed = True
    if node.get("maxTries") != max_tries:
        node["maxTries"] = max_tries
        changed = True
    if node.get("waitBetweenTries") != 1000:
        node["waitBetweenTries"] = 1000
        changed = True
    return changed


def set_writer_system(node: dict) -> bool:
    """Write TriageReport stores system text under messages.messageValues[].message."""
    params = node.setdefault("parameters", {})
    messages = params.setdefault("messages", {})
    values = messages.setdefault("messageValues", [])
    if not values:
        values.append({"message": WRITER_SYSTEM})
        # Also keep legacy options.systemMessage for older node shapes
        opts = params.setdefault("options", {})
        opts["systemMessage"] = WRITER_SYSTEM
        return True
    changed = False
    for entry in values:
        if isinstance(entry, dict) and entry.get("message") != WRITER_SYSTEM:
            entry["message"] = WRITER_SYSTEM
            changed = True
    opts = params.setdefault("options", {})
    if opts.get("systemMessage") != WRITER_SYSTEM:
        opts["systemMessage"] = WRITER_SYSTEM
        changed = True
    return changed


def scrub_for_export(wf: dict) -> dict:
    """Export-safe copy: keep structure, drop active credential ids if present."""
    out = {
        "name": wf.get("name"),
        "nodes": wf.get("nodes", []),
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings") or {},
        "staticData": None,
        "meta": wf.get("meta") or {},
        "pinData": {},
        "versionId": wf.get("versionId"),
        "active": False,
    }
    for node in out["nodes"]:
        creds = node.get("credentials")
        if isinstance(creds, dict):
            for key, val in list(creds.items()):
                if isinstance(val, dict) and "id" in val:
                    val = {k: v for k, v in val.items() if k != "id"}
                    creds[key] = val
        # Drop live webhookId — bootstrap regenerates it
        if node.get("type") == "n8n-nodes-base.webhook" and "webhookId" in node:
            node.pop("webhookId", None)
    return out


def main() -> None:
    wf_id = resolve_workflow_id()
    print(f"target_workflow_id={wf_id}")
    wf = request("GET", f"/workflows/{wf_id}")
    nodes = wf.get("nodes") or []
    changes: list[str] = []

    for node in nodes:
        name = node.get("name", "")
        ntype = node.get("type", "")

        if ntype == OLD_TOOL:
            node["type"] = NEW_TOOL
            changes.append(f"migrate_type:{name}")

        if name in ("Input Passed?", "Output Passed?"):
            if fix_if_left_value(node, "passed"):
                changes.append(f"passed_field:{name}")

        if name == "Reject Signal":
            params = node.setdefault("parameters", {})
            if params.get("responseBody") != REJECT_BODY:
                params["responseBody"] = REJECT_BODY
                changes.append("reject_payload")

        if name in ("Guardrails Input Check", "Guardrails Output Check"):
            if ensure_retries(node, 3):
                changes.append(f"retries:{name}")
            if node.get("onError") != "continueErrorOutput":
                node["onError"] = "continueErrorOutput"
                changes.append(f"onError:{name}")

        if name in ("Predictor Tool", "RAG Query Tool", "LangGraph Agent Tool", "Service Context Tool"):
            if ensure_retries(node, 2):
                changes.append(f"retries:{name}")

        if name == "Write TriageReport":
            if set_writer_system(node):
                changes.append("writer_system")

    if wf.get("description") != DESCRIPTION:
        wf["description"] = DESCRIPTION
        changes.append("description")

    settings = wf.setdefault("settings", {})
    if not settings.get("availableInMCP"):
        settings["availableInMCP"] = True
        changes.append("availableInMCP")

    print("planned_changes=" + json.dumps(changes))
    if not changes:
        print("noop=True")
        return

    allowed_settings = {
        k: v
        for k, v in (settings or {}).items()
        if k
        in {
            "executionOrder",
            "timezone",
            "errorWorkflow",
            "saveManualExecutions",
            "callerPolicy",
            "executionTimeout",
            "timeSavedMode",
            "timeSavedPerExecution",
            "availableInMCP",
        }
    }
    payload = {
        "name": wf["name"],
        "nodes": nodes,
        "connections": wf["connections"],
        "settings": allowed_settings,
        "staticData": wf.get("staticData"),
        "description": DESCRIPTION,
    }
    updated = request("PUT", f"/workflows/{wf_id}", payload)
    print(
        f"updated=True versionId={updated.get('versionId')} "
        f"nodeCount={len(updated.get('nodes') or [])}"
    )

    verify = {n["name"]: n for n in updated.get("nodes") or []}
    for if_name in ("Input Passed?", "Output Passed?"):
        conds = verify[if_name]["parameters"]["conditions"]["conditions"]
        lv = conds[0]["leftValue"]
        print(f"verify_{if_name}={lv}")
    tool_types = {
        n: verify[n]["type"]
        for n in ("Predictor Tool", "RAG Query Tool", "LangGraph Agent Tool")
    }
    print("verify_tool_types=" + json.dumps(tool_types))
    lg = verify["LangGraph Agent Tool"]
    print(
        "verify_langgraph_retries="
        + json.dumps(
            {
                "retryOnFail": lg.get("retryOnFail"),
                "maxTries": lg.get("maxTries"),
            }
        )
    )

    export = scrub_for_export(updated)
    EXPORT_PATH.write_text(json.dumps(export, indent=2) + "\n", encoding="utf-8")
    print(f"exported={EXPORT_PATH}")


if __name__ == "__main__":
    main()
