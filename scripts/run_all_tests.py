"""Run every service's pytest suite from its own rootdir (BUILD_PLAN §2).

Each services/<name>/ is a self-contained import root with its own pytest.ini,
so suites must run per-service — a single repo-root pytest run would collide on
duplicated test module basenames (e.g. test_contracts_identity.py).

Usage:  python scripts/run_all_tests.py  (exit code 1 if any suite fails)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SERVICES_DIR = Path(__file__).resolve().parent.parent / "services"


def main() -> int:
    failures: list[str] = []
    for service in sorted(
        p for p in SERVICES_DIR.iterdir() if (p / "pytest.ini").exists()
    ):
        print(f"=== {service.name} ===", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"], cwd=service, check=False
        )
        if result.returncode != 0:
            failures.append(service.name)
    if failures:
        print(f"FAILED suites: {', '.join(failures)}")
        return 1
    print("All service suites green.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
