#!/usr/bin/env python3
"""Run all AWS AI service course labs (Transcribe, Polly, Textract, Rekognition, Comprehend)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LABS = (
    "transcribe_lab.py",
    "polly_lab.py",
    "textract_lab.py",
    "rekognition_lab.py",
    "comprehend_lab.py",
)


def main() -> int:
    lab_dir = Path(__file__).resolve().parent
    root = lab_dir.parents[1]
    python = root / ".venv" / "Scripts" / "python.exe"
    if not python.is_file():
        python = Path(sys.executable)

    extra = sys.argv[1:]
    failures: list[str] = []
    print(f"Using Python: {python}\n")
    for name in LABS:
        script = lab_dir / name
        print(f"=== {name} ===")
        result = subprocess.run(
            [str(python), str(script), *extra],
            cwd=str(root),
            check=False,
        )
        if result.returncode != 0:
            failures.append(name)
        print()

    if failures:
        print(f"FAILED: {', '.join(failures)}", file=sys.stderr)
        return 1
    print("All labs passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
