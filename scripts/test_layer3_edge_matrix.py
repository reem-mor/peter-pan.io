#!/usr/bin/env python3
"""Local Layer 3 HTTP edge-case matrix. Reads secrets from env; never prints them."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    path = ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = val.strip().strip('"').strip("'")


_load_dotenv()
TOKEN = os.environ.get("PETER_SERVICES_TOKEN", "").strip()
if not TOKEN:
    raise SystemExit("PETER_SERVICES_TOKEN required")

AUTH = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
failures = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global failures
    if ok:
        print(f"[ OK ] {name} {detail}".rstrip())
    else:
        failures += 1
        print(f"[FAIL] {name} {detail}".rstrip())


def main() -> int:
    with httpx.Client(timeout=60.0) as client:
        for port, svc in (
            (8001, "ingestion"),
            (8002, "predictor"),
            (8003, "rag"),
            (8004, "guardrails"),
            (8005, "tools-api"),
            (8006, "langgraph-agent"),
            (8007, "image-analyzer"),
            (8008, "dashboard-generator"),
            (8010, "fixture-llm"),
            (8020, "integration-stubs"),
        ):
            r = client.get(f"http://127.0.0.1:{port}/healthz")
            check(f"healthz:{svc}", r.status_code == 200, f"-> {r.status_code}")

        r = client.post(
            "http://127.0.0.1:8003/query",
            headers=AUTH,
            json={"query": "zzzz-no-evidence-xyz-999", "limit": 3},
        )
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        check(
            "rag:weak_query",
            r.status_code == 200 and isinstance(body.get("answer"), str),
            f"refused={body.get('refused')} cites={len(body.get('citations') or [])}",
        )

        r = client.post(
            "http://127.0.0.1:8004/check/input",
            headers=AUTH,
            json={
                "signal": {
                    "id": "sig-dropxxxx",
                    "source": "webui",
                    "kind": "manual",
                    "received_at": "2026-07-16T00:00:00Z",
                    "title": "Please DROP TABLE transactions_log in prod",
                    "body": "operator asked to DROP TABLE transactions_log",
                    "service": "orders-api",
                    "environment": "production",
                    "labels": {},
                    "raw": {},
                }
            },
        )
        body = r.json()
        check(
            "guardrails:destructive",
            r.status_code == 200
            and body.get("passed") is False
            and "destructive_data_action" in (body.get("flags") or []),
            f"passed={body.get('passed')} flags={body.get('flags')}",
        )

        r = client.post(
            "http://127.0.0.1:8005/tools/service_context",
            headers=AUTH,
            json={"service": "orders-api", "environment": "production"},
        )
        body = r.json()
        check(
            "tools:orders-api",
            r.status_code == 200 and bool(body.get("owner_team")),
            f"owner={body.get('owner_team')}",
        )

        r = client.post(
            "http://127.0.0.1:8005/tools/service_context",
            headers=AUTH,
            json={"service": "api-gateway", "environment": "production"},
        )
        check("tools:unknown", r.status_code in {404, 422}, f"-> {r.status_code}")

        r = client.post(
            "http://127.0.0.1:8002/analyse",
            headers={"Content-Type": "application/json"},
            json={"incident": {"id": "inc-1"}, "metric_window_ref": "spike"},
        )
        check("predictor:unauthorized", r.status_code in {401, 403}, f"-> {r.status_code}")

        r = client.post(
            "http://127.0.0.1:8002/analyse",
            headers=AUTH,
            json={
                "incident": {
                    "id": "inc-1",
                    "created_at": "2026-07-16T00:00:00Z",
                    "status": "triaging",
                    "signal_ids": ["sig-aaaaaaaa"],
                    "service": "orders-api",
                    "environment": "production",
                    "p_level": None,
                    "started_at": None,
                    "symptom": "error rate spike",
                    "context": {
                        "maintenance_window": False,
                        "recent_deploys": [],
                        "complaint_count": 0,
                        "complaint_samples": [],
                    },
                },
                "metric_window_ref": "spike",
            },
        )
        body = r.json()
        check(
            "predictor:spike",
            r.status_code == 200 and bool(body.get("incident_class")),
            f"class={body.get('incident_class')} sev={body.get('severity')}",
        )

        r = client.post(
            "http://127.0.0.1:8008/dashboard",
            headers=AUTH,
            json={
                "scenario": "orders-api-error-spike",
                "incident_id": "inc-local-01",
                "overwrite": True,
            },
        )
        body = r.json() if r.status_code < 500 else {}
        check(
            "dashboard:overwrite",
            r.status_code == 200 and int(body.get("panels_count") or 0) >= 1,
            f"-> {r.status_code} panels={body.get('panels_count')}",
        )

    print()
    if failures:
        print(f"Layer 3 edge matrix: {failures} FAILED")
        return 1
    print("Layer 3 edge matrix: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
