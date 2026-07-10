"""Validate the corpus structure (JSON docs) and the kb_manifest grouping."""

from __future__ import annotations

from rag_service.kb_corpus import (
    KB_ROOT,
    REQUIRED_DOC_KEYS,
    VALID_DOC_TYPES,
    iter_corpus_json_paths,
    load_kb_document,
)
from rag_service.kb_manifest import kb_sections

REQUIRED_DIRS = {"runbooks", "incidents", "services"}


def test_knowledge_base_has_authoritative_sections():
    assert REQUIRED_DIRS <= {path.name for path in KB_ROOT.iterdir() if path.is_dir()}


def test_knowledge_base_json_has_required_fields():
    docs = list(iter_corpus_json_paths())
    assert docs
    for path in docs:
        doc = load_kb_document(path)
        assert REQUIRED_DOC_KEYS <= set(doc), f"{path} missing keys"
        assert doc["doc_type"] in VALID_DOC_TYPES


def test_knowledge_base_doc_ids_are_unique():
    docs = [load_kb_document(p) for p in iter_corpus_json_paths()]
    doc_ids = [doc["doc_id"] for doc in docs]
    assert len(doc_ids) == len(set(doc_ids))


def test_kb_sections_groups_documents_by_doc_type():
    sections = kb_sections()
    assert sections["runbooks"]
    assert sections["incidents"]
    assert sections["services"]
    for doc in sections["runbooks"]:
        assert doc["doc_type"] == "runbook"
    for doc in sections["incidents"]:
        assert doc["doc_type"] == "incident"
    for doc in sections["services"]:
        assert doc["doc_type"] == "service"
