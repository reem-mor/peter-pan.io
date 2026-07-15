#!/usr/bin/env python3
"""Public + on-instance health evidence for EC2 deploy verification."""
from __future__ import annotations

import subprocess
import sys

import httpx

IP = sys.argv[1] if len(sys.argv) > 1 else __import__("os").environ.get("EC2_PUBLIC_IP", "").strip()
if not IP:
    raise SystemExit("Usage: python scripts/test_ec2_public_health.py <EC2_PUBLIC_IP>")
BASE = f"http://{IP}"
KEY = __import__("os").path.expanduser("~/.ssh/peter-pan-key.pem")

PORTS: dict[str, int] = {
    "ingestion": 8001,
    "predictor": 8002,
    "rag": 8003,
    "guardrails": 8004,
    "tools-api": 8005,
    "langgraph-agent": 8006,
    "dashboard-generator": 8008,
    "image-analyzer": 8007,
    "integration-stubs": 8020,
    "fixture-llm": 8010,
}

# Services intentionally bound to loopback on the demo host (n8n reaches them
# on the compose network). Public health probes use SSH instead.
LOOPBACK_ONLY = frozenset({"fixture-llm", "rag"})

failures = 0
with httpx.Client(timeout=10.0) as client:
    for name, port in PORTS.items():
        if name in LOOPBACK_ONLY:
            continue
        url = f"{BASE}:{port}/healthz"
        try:
            resp = client.get(url)
            ok = resp.status_code == 200
        except httpx.HTTPError as exc:
            failures += 1
            print(f"[FAIL] {name:18s} {url} -> {exc}")
            continue
        if ok:
            print(f"[ OK ] {name:18s} {url} -> 200")
        else:
            failures += 1
            print(f"[FAIL] {name:18s} {url} -> {resp.status_code}")

    grafana_url = f"{BASE}:3000/api/health"
    try:
        resp = client.get(grafana_url)
        if resp.status_code == 200:
            print(f"[ OK ] grafana            {grafana_url} -> 200")
        else:
            failures += 1
            print(f"[FAIL] grafana            {grafana_url} -> {resp.status_code}")
    except httpx.HTTPError as exc:
        failures += 1
        print(f"[FAIL] grafana            {grafana_url} -> {exc}")

# fixture-llm + rag: loopback-only on the demo host (n8n uses compose DNS).
ssh_cmd = [
    "ssh",
    "-i",
    KEY,
    "-o",
    "StrictHostKeyChecking=accept-new",
    f"ubuntu@{IP}",
    "printf 'fixture-llm='; curl -s -o /dev/null -w '%{http_code}' "
    "http://localhost:8010/healthz; printf ' rag='; "
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:8003/healthz",
]
try:
    codes = subprocess.check_output(ssh_cmd, text=True).strip()
    parts = dict(
        item.split("=", 1) for item in codes.split() if "=" in item
    )
    for name in ("fixture-llm", "rag"):
        code = parts.get(name, "missing")
        port = PORTS[name]
        if code == "200":
            print(
                f"[ OK ] {name:18s}"
                f"http://localhost:{port}/healthz (on-instance loopback) -> 200"
            )
        else:
            failures += 1
            print(
                f"[FAIL] {name:18s}"
                f"http://localhost:{port}/healthz (on-instance loopback) -> {code}"
            )
except (subprocess.CalledProcessError, FileNotFoundError) as exc:
    failures += 1
    print(f"[FAIL] fixture-llm        on-instance loopback check -> {exc}")

print()
if failures:
    print(f"Public health: {failures} FAILED")
    raise SystemExit(1)
print("Public health: all 10 services + Grafana healthy")
raise SystemExit(0)
