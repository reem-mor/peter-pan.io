#!/usr/bin/env python3
"""Bootstrap local n8n: import workflow, credentials, activate webhook."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "n8n" / "peter-flow.json"
WORKFLOW_NAME = "PETER PAN — PETER Flow (Stage A)"
COMPOSE_SERVICE = "n8n"

N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "http://127.0.0.1:5678").rstrip("/")
OWNER_EMAIL = os.environ.get("N8N_OWNER_EMAIL", "admin@local.peter")
OWNER_PASSWORD = os.environ.get("N8N_OWNER_PASSWORD", "").strip()
SERVICES_TOKEN = os.environ.get("PETER_SERVICES_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("PETER_WEBHOOK_SECRET", "").strip()
FIXTURE_LLM_API_KEY = os.environ.get(
    "PETER_FIXTURE_LLM_API_KEY",
    SERVICES_TOKEN,
).strip()
FIXTURE_LLM_INTERNAL_URL = os.environ.get(
    "PETER_FIXTURE_LLM_URL", "http://fixture-llm:8000/v1"
)
USE_CLI_IMPORT = os.environ.get("N8N_BOOTSTRAP_CLI_IMPORT", "0") == "1"


def _wait_for_n8n(client: httpx.Client, timeout_s: int = 120) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            response = client.get("/healthz", timeout=5.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(2)
    raise TimeoutError("n8n not healthy within timeout")


def _ensure_owner(client: httpx.Client) -> None:
    login = client.post(
        "/rest/login",
        json={"emailOrLdapLoginId": OWNER_EMAIL, "password": OWNER_PASSWORD},
    )
    if login.status_code == 200 and login.json().get("data"):
        return

    setup = client.post(
        "/rest/owner/setup",
        json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD,
            "firstName": "PETER",
            "lastName": "PAN",
        },
    )
    if setup.status_code not in {200, 201, 409}:
        message = setup.json().get("message", setup.text) if setup.content else setup.text
        if not (isinstance(message, str) and "already" in message.lower()):
            raise RuntimeError(f"n8n owner setup failed: {setup.status_code} {message}")

    login = client.post(
        "/rest/login",
        json={"emailOrLdapLoginId": OWNER_EMAIL, "password": OWNER_PASSWORD},
    )
    if login.status_code != 200 or not login.json().get("data"):
        raise RuntimeError(f"n8n login failed: {login.status_code} {login.text}")


def _credential_id(client: httpx.Client, name: str, create_payload: dict[str, Any]) -> str:
    listing = client.get("/rest/credentials")
    listing.raise_for_status()
    for item in listing.json().get("data", []):
        if item.get("name") == name:
            return item["id"]

    created = client.post("/rest/credentials", json=create_payload)
    created.raise_for_status()
    return created.json()["data"]["id"]


def _delete_workflow(client: httpx.Client, workflow_id: str) -> None:
    deactivated = client.post(f"/rest/workflows/{workflow_id}/deactivate")
    if deactivated.status_code not in {200, 400, 404}:
        raise RuntimeError(
            f"workflow deactivate failed: {deactivated.status_code} {deactivated.text}"
        )
    archived = client.post(f"/rest/workflows/{workflow_id}/archive")
    if archived.status_code >= 400 and "already archived" not in archived.text.lower():
        raise RuntimeError(
            f"workflow archive failed: {archived.status_code} {archived.text}"
        )
    deleted = client.delete(f"/rest/workflows/{workflow_id}")
    if deleted.status_code not in {200, 204, 404}:
        raise RuntimeError(
            f"workflow delete failed: {deleted.status_code} {deleted.text}"
        )


def _import_workflow_cli() -> None:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            COMPOSE_SERVICE,
            "n8n",
            "import:workflow",
            "--input=/import/peter-flow.json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stderr.strip():
        print(result.stderr.strip())


def _import_workflow_api(client: httpx.Client) -> None:
    payload = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    body = {
        "name": payload["name"],
        "nodes": payload["nodes"],
        "connections": payload["connections"],
        "settings": payload.get("settings", {}),
        "active": False,
    }
    created = client.post("/rest/workflows", json=body)
    if created.status_code not in {200, 201}:
        raise RuntimeError(f"workflow import failed: {created.status_code} {created.text}")


def _purge_named_workflows(client: httpx.Client) -> None:
    listing = client.get("/rest/workflows")
    listing.raise_for_status()
    for summary in listing.json().get("data", []):
        if summary.get("name") != WORKFLOW_NAME:
            continue
        print("Replacing existing PETER workflow ...")
        _delete_workflow(client, summary["id"])


def _find_workflow(client: httpx.Client) -> dict[str, Any] | None:
    listing = client.get("/rest/workflows")
    listing.raise_for_status()
    summary = next(
        (
            w
            for w in listing.json().get("data", [])
            if w.get("name") == WORKFLOW_NAME and not w.get("isArchived")
        ),
        None,
    )
    if summary is None:
        return None
    detail = client.get(f"/rest/workflows/{summary['id']}")
    detail.raise_for_status()
    return detail.json().get("data") or detail.json()


def _publish_workflow(
    client: httpx.Client,
    *,
    workflow_id: str,
    version_id: str,
) -> None:
    published = client.post(
        f"/rest/workflows/{workflow_id}/activate",
        json={"versionId": version_id},
    )
    if published.status_code != 200:
        raise RuntimeError(
            f"workflow publish failed: {published.status_code} {published.text}"
        )


def _patch_and_activate(
    client: httpx.Client,
    bearer_id: str,
    openai_id: str,
    webhook_auth_id: str,
) -> str:
    workflow = _find_workflow(client)
    if workflow is None:
        raise RuntimeError(f"workflow '{WORKFLOW_NAME}' not found after import")

    nodes = workflow.get("nodes", [])
    for node in nodes:
        params = node.get("parameters", {})
        if params.get("genericAuthType") == "httpBearerAuth":
            node["credentials"] = {
                "httpBearerAuth": {"id": bearer_id, "name": "PETER Services Bearer"}
            }
        if node.get("type") == "@n8n/n8n-nodes-langchain.lmChatOpenAi":
            node["credentials"] = {
                "openAiApi": {
                    "id": openai_id,
                    "name": "PETER Mock LLM (OpenAI-compatible)",
                }
            }
        if (
            node.get("type") == "n8n-nodes-base.webhook"
            and params.get("authentication") == "headerAuth"
        ):
            node["credentials"] = {
                "httpHeaderAuth": {
                    "id": webhook_auth_id,
                    "name": "PETER Webhook Header",
                }
            }

    workflow_id = workflow["id"]
    patch = client.patch(
        f"/rest/workflows/{workflow_id}",
        json={
            "name": workflow["name"],
            "nodes": nodes,
            "connections": workflow["connections"],
            "settings": workflow.get("settings", {}),
        },
    )
    if patch.status_code >= 400:
        raise RuntimeError(
            f"workflow patch failed: {patch.status_code} {patch.text}"
        )

    updated = _find_workflow(client)
    if updated is None or not updated.get("versionId"):
        raise RuntimeError("workflow version missing after credential patch")
    _publish_workflow(
        client,
        workflow_id=workflow_id,
        version_id=updated["versionId"],
    )
    return workflow_id


def main() -> int:
    if not OWNER_PASSWORD:
        raise RuntimeError(
            "N8N_OWNER_PASSWORD is required — set it in .env (see .env.example)"
        )
    if not SERVICES_TOKEN.strip():
        raise RuntimeError(
            "PETER_SERVICES_TOKEN is required — set it in .env (see .env.example)"
        )
    if not WEBHOOK_SECRET:
        raise RuntimeError(
            "PETER_WEBHOOK_SECRET is required — set it in .env (see .env.example)"
        )
    print(f"Waiting for n8n at {N8N_BASE_URL} ...")
    with httpx.Client(base_url=N8N_BASE_URL, timeout=30.0) as client:
        _wait_for_n8n(client)
        print("Ensuring owner + session ...")
        _ensure_owner(client)

        existing = _find_workflow(client)
        if existing and existing.get("active"):
            print("Workflow already active; skipping bootstrap")
            return 0

        if existing or any(
            w.get("name") == WORKFLOW_NAME
            for w in client.get("/rest/workflows").json().get("data", [])
        ):
            _purge_named_workflows(client)

        print("Creating credentials ...")
        bearer_id = _credential_id(
            client,
            "PETER Services Bearer",
            {
                "name": "PETER Services Bearer",
                "type": "httpBearerAuth",
                "data": {"token": SERVICES_TOKEN},
            },
        )
        openai_id = _credential_id(
            client,
            "PETER Mock LLM (OpenAI-compatible)",
            {
                "name": "PETER Mock LLM (OpenAI-compatible)",
                "type": "openAiApi",
                "data": {"apiKey": FIXTURE_LLM_API_KEY, "url": FIXTURE_LLM_INTERNAL_URL},
            },
        )
        webhook_auth_id = _credential_id(
            client,
            "PETER Webhook Header",
            {
                "name": "PETER Webhook Header",
                "type": "httpHeaderAuth",
                "data": {
                    "name": "X-Peter-Webhook-Secret",
                    "value": WEBHOOK_SECRET,
                },
            },
        )

        print("Importing workflow ...")
        if USE_CLI_IMPORT:
            try:
                _import_workflow_cli()
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("CLI import unavailable; falling back to REST import")
                _import_workflow_api(client)
        else:
            _import_workflow_api(client)

        print("Activating workflow ...")
        _patch_and_activate(
            client,
            bearer_id,
            openai_id,
            webhook_auth_id,
        )
        print("Activated PETER workflow")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"bootstrap failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
