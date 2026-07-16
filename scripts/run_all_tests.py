"""Run every test suite from its own rootdir (BUILD_PLAN §2).

Each services/<name>/ is a self-contained import root with its own pytest.ini,
so suites must run per-service — a single repo-root pytest run would collide on
duplicated test module basenames (e.g. test_contracts_identity.py).

Additional suites (observability package, ui/, n8n/, evaluation/) are included
automatically when they have a pytest.ini or a tests/ directory.

Usage:  python scripts/run_all_tests.py  (exit code 1 if any suite fails)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence

_REPO_ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = _REPO_ROOT / "services"

# Extra top-level suites appended after services, in declaration order.
EXTRA_SUITE_DIRS: list[Path] = [
    _REPO_ROOT / "packages" / "peter_observability",
    _REPO_ROOT / "ui",
    _REPO_ROOT / "n8n",
    _REPO_ROOT / "evaluation",
]


def _resolve_python() -> str:
    """Prefer the repo .venv interpreter so bare `python scripts/...` works."""
    if sys.platform == "win32":
        candidates = (_REPO_ROOT / ".venv" / "Scripts" / "python.exe",)
    else:
        candidates = (_REPO_ROOT / ".venv" / "bin" / "python",)
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def _has_pytest_suite(p: Path) -> bool:
    """Return True if *p* looks like a pytest suite (pytest.ini or tests/ dir present)."""
    if not p.exists():
        return False
    return (p / "pytest.ini").exists() or (p / "tests").is_dir()


def _iter_suites(
    services_dir: Path,
    extra_dirs: Sequence[Path],
) -> list[Path]:
    """Return ordered list of directories to run pytest in.

    Services come first (sorted), then extra suites in declaration order.
    A directory is included only when it exists and has pytest infrastructure.
    """
    suites: list[Path] = []

    if services_dir.exists():
        suites.extend(
            sorted(p for p in services_dir.iterdir() if (p / "pytest.ini").exists())
        )

    for extra in extra_dirs:
        if _has_pytest_suite(extra):
            suites.append(extra)

    return suites


def main(
    services_dir: Path | None = None,
    extra_suite_dirs: Sequence[Path] | None = None,
) -> int:
    """Run all discovered suites; return 0 on full success, 1 on any failure."""
    if services_dir is None:
        services_dir = SERVICES_DIR
    if extra_suite_dirs is None:
        extra_suite_dirs = EXTRA_SUITE_DIRS

    suites = _iter_suites(services_dir, extra_suite_dirs)
    if not suites:
        print("FAILED: no pytest suites discovered")
        return 1

    failures: list[str] = []
    python = _resolve_python()

    for suite in suites:
        print(f"=== {suite.name} ===", flush=True)
        result = subprocess.run(
            [python, "-m", "pytest", "-q"],
            cwd=suite,
            check=False,
        )
        if result.returncode != 0:
            failures.append(suite.name)

    if failures:
        print(f"FAILED suites: {', '.join(failures)}")
        return 1

    print("All suites green.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
