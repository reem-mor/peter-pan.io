"""Tests for the GGUF insight generator seam (mocked — no live llama.cpp)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from rag_service import generator as gen_mod
from rag_service.generator import (
    LlamaGenerator,
    build_prompt,
    get_generator,
    system_prompt,
)


def test_system_prompt_matches_vendored_file():
    vendored = (
        Path(__file__).resolve().parents[1]
        / "rag_service"
        / "prompts"
        / "surface-3-rag.systemprompt.txt"
    )
    assert system_prompt() == vendored.read_text(encoding="utf-8")


def test_build_prompt_includes_documents_and_question():
    prompt = build_prompt(
        "postgres pool exhausted",
        ["(per INC-111, P1, postgres-primary) pool saturated"],
    )
    assert "Operator question: postgres pool exhausted" in prompt
    assert "[document 1]" in prompt
    assert system_prompt() in prompt


def test_build_prompt_truncates_long_documents():
    long_excerpt = "x" * 10_000
    prompt = build_prompt("short question", [long_excerpt])
    assert len(prompt) < len(long_excerpt) + 500


def test_llama_generator_returns_text_from_mock():
    def _mock_llm(prompt: str, **kwargs: Any) -> dict:
        return {"choices": [{"text": "Similar to INC-101 (per INC-101)."}]}

    generator = LlamaGenerator(_mock_llm)
    result = generator.generate("orders error spike", ["doc one"])
    assert result == "Similar to INC-101 (per INC-101)."


def test_llama_generator_returns_none_on_bad_response():
    def _bad_llm(prompt: str, **kwargs: Any) -> dict:
        return {"choices": []}

    generator = LlamaGenerator(_bad_llm)
    assert generator.generate("q", ["doc"]) is None


def test_get_generator_none_when_env_unset(monkeypatch):
    monkeypatch.delenv("GGUF_MODEL_PATH", raising=False)
    gen_mod._cached.clear()
    assert get_generator() is None


def test_get_generator_none_when_file_missing(monkeypatch, tmp_path):
    missing = tmp_path / "missing.gguf"
    monkeypatch.setenv("GGUF_MODEL_PATH", str(missing))
    gen_mod._cached.clear()
    assert get_generator() is None


def test_get_generator_uses_cached_instance(monkeypatch, tmp_path):
    fake = tmp_path / "model.gguf"
    fake.write_bytes(b"fake")

    class _Llama:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def __call__(self, prompt: str, **kwargs: Any) -> dict:
            return {"choices": [{"text": "insight"}]}

    monkeypatch.setenv("GGUF_MODEL_PATH", str(fake))
    monkeypatch.setitem(__import__("sys").modules, "llama_cpp", type("m", (), {"Llama": _Llama}))
    gen_mod._cached.clear()
    first = get_generator()
    second = get_generator()
    assert first is second
    assert first is not None
