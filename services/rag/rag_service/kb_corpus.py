"""Load the PETER PAN RAG corpus (JSON documents under ``corpus/``).

Self-contained per AGENTS.md §2: the corpus root defaults to a directory
inside this service (``services/rag/corpus``) and can be overridden with the
``RAG_CORPUS_DIR`` env var (e.g. for tests or an alternate deployment).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

_DEFAULT_CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"
KB_ROOT = Path(os.environ.get("RAG_CORPUS_DIR", str(_DEFAULT_CORPUS_DIR)))

# The narrative corpus lives only in these subdirectories.
DOC_SUBDIRS = ("runbooks", "incidents", "services")

REQUIRED_DOC_KEYS = {
    "doc_id",
    "title",
    "doc_type",
    "services",
    "environments",
    "severity_applicable",
    "tags",
    "last_updated",
    "author",
    "version",
    "body",
}
VALID_DOC_TYPES = {"runbook", "policy", "incident", "service", "guide", "reference"}
CORPUS_JSON_GLOB = "*.json"


def kb_root() -> Path:
    return KB_ROOT


def iter_corpus_json_paths(*, root: Path | None = None) -> Iterator[Path]:
    """Yield narrative corpus document JSON files from the doc subdirectories only.

    Excludes anything at the corpus root and any README.json so only
    grounding-worthy narrative docs are indexed.
    """
    base = root or KB_ROOT
    if not base.is_dir():
        return
    for sub in DOC_SUBDIRS:
        sub_dir = base / sub
        if not sub_dir.is_dir():
            continue
        for path in sorted(sub_dir.rglob(CORPUS_JSON_GLOB)):
            if path.is_file() and path.name != "README.json":
                yield path


def load_kb_document(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    missing = REQUIRED_DOC_KEYS - set(data)
    if missing:
        raise ValueError(f"{path} missing keys: {sorted(missing)}")
    dtype = str(data["doc_type"]).strip()
    if dtype not in VALID_DOC_TYPES:
        raise ValueError(f"{path} invalid doc_type: {dtype!r}")
    return data


def document_text(doc: dict[str, Any]) -> str:
    """Text used for chunking / retrieval (title + body)."""
    title = str(doc.get("title", "")).strip()
    body = str(doc.get("body", "")).strip()
    if title and body:
        return f"# {title}\n\n{body}"
    return title or body


@lru_cache(maxsize=1)
def load_kb_manifest() -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for path in iter_corpus_json_paths():
        doc = load_kb_document(path)
        rel = path.relative_to(KB_ROOT).as_posix()
        docs.append(
            {
                "id": rel,
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "doc_type": doc["doc_type"],
                "services": doc["services"],
                "environments": doc["environments"],
                "severity_applicable": doc["severity_applicable"],
                "tags": doc["tags"],
                "last_updated": doc["last_updated"],
                "author": doc["author"],
                "version": doc["version"],
                "format": "json",
                "indexed": True,
                "sync_status": "indexed",
            }
        )
    return docs
