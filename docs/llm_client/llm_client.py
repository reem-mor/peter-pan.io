"""Canonical LLM client seam — vendored into services that need generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol

TaskKind = Literal["extract", "agent", "synthesis", "rag_generate", "assistant"]


@dataclass(frozen=True)
class LLMResult:
    text: str
    task: TaskKind
    fixture_id: str | None = None
    model_meta: dict[str, str] | None = None


class LLMClient(Protocol):
    def complete(
        self,
        *,
        task: TaskKind,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> LLMResult: ...


class FixtureLLMClient:
    """Deterministic canned responses keyed by task."""

    _RESPONSES: dict[TaskKind, str] = {
        "extract": '{"service":"orders-api","symptom":"elevated errors"}',
        "agent": "Call RAG, Predictor, and LangGraph before synthesis.",
        "synthesis": '{"incident_id":"inc-fixture001","category":"application","p_level":"P3"}',
        "rag_generate": "Cited runbook excerpt only.",
        "assistant": "I support incident triage for demo services only.",
    }

    def complete(
        self,
        *,
        task: TaskKind,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> LLMResult:
        return LLMResult(
            text=self._RESPONSES[task],
            task=task,
            fixture_id=f"fixture-{task}",
            model_meta={"provider": "fixture", "stage": "A"},
        )


class BedrockLLMClient:
    """Stage C adapter stub — raises until configured."""

    def complete(
        self,
        *,
        task: TaskKind,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> LLMResult:
        raise RuntimeError(
            "BedrockLLMClient requires PETER_LLM_PROVIDER=bedrock and AWS credentials"
        )


class GeminiLLMClient:
    """Stage C adapter stub — raises until configured."""

    def complete(
        self,
        *,
        task: TaskKind,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> LLMResult:
        raise RuntimeError(
            "GeminiLLMClient requires PETER_LLM_PROVIDER=gemini and API credentials"
        )


class OllamaLLMClient:
    """Stage C adapter stub — raises until configured."""

    def complete(
        self,
        *,
        task: TaskKind,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> LLMResult:
        raise RuntimeError(
            "OllamaLLMClient requires PETER_LLM_PROVIDER=ollama and PETER_OLLAMA_URL"
        )


def build_llm_client(provider: str) -> LLMClient:
    if provider == "fixture":
        return FixtureLLMClient()
    if provider == "bedrock":
        return BedrockLLMClient()
    if provider == "gemini":
        return GeminiLLMClient()
    if provider == "ollama":
        return OllamaLLMClient()
    raise ValueError(f"unsupported LLM provider: {provider}")
