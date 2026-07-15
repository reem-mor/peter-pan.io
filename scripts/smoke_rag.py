"""Manual RAG smoke: real ChromaDB retrieval + real GGUF generation.

NOT part of CI (both heavy paths are mocked there). Run on a box with the
vector store populated and a GGUF model downloaded::

    set GGUF_MODEL_PATH=C:\\dev\\models\\mistral-7b-instruct-v0.2.Q4_K_M.gguf
    python scripts/smoke_rag.py "postgres connection pool exhausted, deadlocks"

Exit codes: 0 = grounded insight produced; 1 = a required component missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "services" / "rag"))

from rag_service.generator import get_generator  # noqa: E402
from rag_service.vector_rag import get_vector_retriever  # noqa: E402

DEFAULT_QUERY = "orders-api 5xx error rate surge right after a release"


def main() -> int:
    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY

    retriever = get_vector_retriever()
    if retriever is None:
        print("FAIL: chroma retriever unavailable (populate the store first)")
        return 1
    hits = retriever.search(query, top_k=3)
    print(f"query: {query}")
    print(f"hits: {[(hit.doc_id, hit.score) for hit in hits]}")
    if not hits:
        print("no grounded hits — the honest refusal path would trigger")
        return 0

    generator = get_generator()
    if generator is None:
        print("FAIL: GGUF generator unavailable (set GGUF_MODEL_PATH; "
              "pip install llama-cpp-python)")
        return 1
    insight = generator.generate(query, [hit.excerpt for hit in hits])
    print("--- insight ---")
    print(insight or "(empty generation)")
    return 0 if insight else 1


if __name__ == "__main__":
    raise SystemExit(main())
