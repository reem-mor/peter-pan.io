"""Populate the RAG incident vector store (rubric deliverable).

Seeded and idempotent: incidents come from the committed, reviewable
``services/rag/data/incidents_seed.json`` with deterministic ``incident_id``s,
and records are UPSERTed by id — running the script twice yields the same
count. The collection stores which embedding model built it; the RAG service
refuses to query on a mismatch.

Usage (repo venv, chromadb + sentence-transformers installed)::

    python scripts/populate_vector_store.py [--chroma-path PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAG_SERVICE_DIR = REPO_ROOT / "services" / "rag"
SEED_PATH = RAG_SERVICE_DIR / "data" / "incidents_seed.json"

sys.path.insert(0, str(RAG_SERVICE_DIR))

from rag_service.vector_rag import (  # noqa: E402
    COLLECTION_NAME,
    EMBED_MODEL_METADATA_KEY,
    EMBED_MODEL_NAME,
    chroma_path,
)

MIN_INCIDENTS = 20
MIN_PER_CLASS = 3


def load_seed() -> list[dict]:
    incidents = json.loads(SEED_PATH.read_text(encoding="utf-8"))["incidents"]
    per_class = Counter(item["incident_class"] for item in incidents)
    ids = [item["incident_id"] for item in incidents]
    if len(ids) != len(set(ids)):
        raise SystemExit("seed error: duplicate incident_ids")
    if len(incidents) < MIN_INCIDENTS:
        raise SystemExit(f"seed error: {len(incidents)} incidents < {MIN_INCIDENTS}")
    short = {c: n for c, n in per_class.items() if n < MIN_PER_CLASS}
    if short:
        raise SystemExit(f"seed error: classes below {MIN_PER_CLASS} records: {short}")
    print(f"seed: {len(incidents)} incidents, per-class {dict(per_class)}")
    return incidents


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chroma-path", default=None)
    args = parser.parse_args()

    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SystemExit(
            f"missing dependency ({exc.name}): pip install chromadb sentence-transformers"
        ) from exc

    incidents = load_seed()
    store_path = Path(args.chroma_path) if args.chroma_path else chroma_path()
    store_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(store_path))
    collection = client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={
            EMBED_MODEL_METADATA_KEY: EMBED_MODEL_NAME,
            "hnsw:space": "cosine",
        },
    )
    before = collection.count()

    embedder = SentenceTransformer(EMBED_MODEL_NAME)
    texts = [item["text"] for item in incidents]
    embeddings = embedder.encode(texts, normalize_embeddings=True)

    collection.upsert(
        ids=[item["incident_id"] for item in incidents],
        documents=texts,
        embeddings=[list(map(float, vector)) for vector in embeddings],
        metadatas=[
            {
                "incident_id": item["incident_id"],
                "incident_class": item["incident_class"],
                "severity": item["severity"],
                "service": item["service"],
                "resolution_summary": item["resolution_summary"],
            }
            for item in incidents
        ],
    )
    after = collection.count()
    print(
        f"collection '{COLLECTION_NAME}' at {store_path}: "
        f"count {before} -> {after} (embedding model: {EMBED_MODEL_NAME})"
    )


if __name__ == "__main__":
    main()
