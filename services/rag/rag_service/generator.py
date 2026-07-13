"""llama.cpp GGUF insight generation behind a fakeable seam.

Loaded once at first use from ``GGUF_MODEL_PATH`` (Q4_K_M 7B fits t3.large
RAM; document the exact file+quant in deployment notes). Every failure mode —
env unset, file missing, llama-cpp-python not installed — returns ``None`` and
the query route keeps the deterministic extractive answer (fixture-first: the
demo path never depends on the model). CI mocks this module; the real path is
exercised manually via ``scripts/smoke_rag.py``.

The system prompt is prompt surface #3 — vendored here and byte-matched
against ``docs/prompt-log/prompts/surface-3-rag.systemprompt.txt`` by a test.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "surface-3-rag.systemprompt.txt"

# Grounded synthesis, not creative writing.
TEMPERATURE = 0.2
MAX_TOKENS = 300
# Context budget in characters for the document block; on overflow the
# DOCUMENTS are truncated (weakest-scored first, i.e. from the end of the
# top-k list), never the operator's question.
MAX_DOCS_CHARS = 6000
N_CTX = 4096


def system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_prompt(question: str, excerpts: list[str]) -> str:
    """Assemble system prompt + retrieved documents + question."""
    docs: list[str] = []
    budget = MAX_DOCS_CHARS
    for index, excerpt in enumerate(excerpts, start=1):
        text = excerpt.strip()
        if len(text) > budget:
            text = text[: max(0, budget)]
        if not text:
            break
        docs.append(f"[document {index}]\n{text}")
        budget -= len(text)
        if budget <= 0:
            break
    doc_block = "\n\n".join(docs) if docs else "(no documents retrieved)"
    return (
        f"{system_prompt()}\n"
        f"Retrieved incident documents:\n{doc_block}\n\n"
        f"Operator question: {question.strip()}\n"
        f"Insight:"
    )


class CompletionModel(Protocol):
    def __call__(self, prompt: str, **kwargs: Any) -> dict: ...


class LlamaGenerator:
    """Wraps a llama.cpp completion callable (injectable for tests)."""

    def __init__(self, llm: CompletionModel) -> None:
        self._llm = llm

    def generate(self, question: str, excerpts: list[str]) -> str | None:
        prompt = build_prompt(question, excerpts)
        try:
            result = self._llm(
                prompt,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stop=["Operator question:", "[document"],
            )
            text = result["choices"][0]["text"].strip()
        except (KeyError, IndexError, RuntimeError, ValueError) as exc:
            logger.error("GGUF generation failed: %s — using extractive answer", exc)
            return None
        return text or None


_cached: dict[str, LlamaGenerator | None] = {}


def get_generator() -> LlamaGenerator | None:
    """Cached loader; ``None`` = keep the deterministic extractive answer."""
    path = os.environ.get("GGUF_MODEL_PATH", "")
    if not path:
        return None
    if path not in _cached:
        _cached[path] = _load(path)
    return _cached[path]


def _load(path: str) -> LlamaGenerator | None:
    if not Path(path).is_file():
        logger.error("GGUF_MODEL_PATH set but file missing: %s", path)
        return None
    try:
        from llama_cpp import Llama
    except ImportError:
        logger.error(
            "GGUF_MODEL_PATH set but llama-cpp-python is not installed "
            "— using extractive answers"
        )
        return None
    logger.info("loading GGUF model from %s (n_ctx=%d)", path, N_CTX)
    llm = Llama(model_path=path, n_ctx=N_CTX, verbose=False)
    return LlamaGenerator(llm)
