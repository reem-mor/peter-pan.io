#!/usr/bin/env python3
"""Layer 3 health validation — ping /healthz on all six core services.

Usage:
  python scripts/test_layer3_health.py                         # local compose
  python scripts/test_layer3_health.py --base-url http://<ec2-ip>
  python scripts/test_layer3_health.py --include-support       # + image/stub seams
"""

from __future__ import annotations

import argparse

import httpx

CORE_PORTS: dict[str, int] = {
    "ingestion": 8001,
    "predictor": 8002,
    "rag": 8003,
    "guardrails": 8004,
    "tools-api": 8005,
    "langgraph-agent": 8006,
}
SUPPORT_PORTS: dict[str, int] = {
    "image-analyzer": 8007,
    "integration-stubs": 8020,
    "fixture-llm": 8010,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PETER PAN Layer 3 health check")
    parser.add_argument("--base-url", default="http://localhost", help="Host base URL")
    parser.add_argument(
        "--timeout", type=float, default=5.0, help="Per-request timeout (s)"
    )
    parser.add_argument(
        "--include-support",
        action="store_true",
        help="Also check image-analyzer, integration-stubs, and fixture-llm (local/on-instance only)",
    )
    args = parser.parse_args(argv)

    targets = dict(CORE_PORTS)
    if args.include_support:
        targets.update(SUPPORT_PORTS)

    base = args.base_url.rstrip("/")
    failures: list[str] = []
    with httpx.Client(timeout=args.timeout) as client:
        for name, port in targets.items():
            url = f"{base}:{port}/healthz"
            try:
                response = client.get(url)
                ok = response.status_code == 200
            except httpx.HTTPError as exc:
                failures.append(f"{name}: unreachable ({exc})")
                print(f"[FAIL] {name:18s} {url} -> {exc}")
                continue
            if ok:
                print(f"[ OK ] {name:18s} {url} -> 200")
            else:
                failures.append(f"{name}: HTTP {response.status_code}")
                print(f"[FAIL] {name:18s} {url} -> {response.status_code}")

    print()
    if failures:
        print(f"Layer 3 health: {len(failures)}/{len(targets)} FAILED")
        return 1
    print(f"Layer 3 health: all {len(targets)} services healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
