"""Evaluation test configuration — add evaluation/ to sys.path so tests can
import run_e2e without making it a package (which would break the existing
``python evaluation/run_e2e.py`` invocation)."""

import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent.parent
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))
