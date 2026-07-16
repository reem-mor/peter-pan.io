# Layer 4 — Model tier (`LLMClient`)

Task-routed LLM seam for PETER PAN. Canonical protocol lives in
[`llm_client.py`](llm_client.py). Services may vendor a copy; do not invent a
second protocol.

## Providers

| Client | Role | Demo dependency? |
|:---|:---|:---|
| `FixtureLLMClient` | Deterministic Stage A responses via Fixture LLM HTTP | **Yes** (golden path) |
| `BedrockLLMClient` | Claude on Amazon Bedrock | Optional Stage C |
| `GeminiLLMClient` | Gemini for extraction / agent | Optional Stage C |
| `OllamaLLMClient` | Local models for WebUI assistant | Optional Stage C |

RAG generation may additionally use **Llama.cpp + GGUF** inside the RAG service
(`GGUF_MODEL_PATH`) — same Layer 4 idea, owned by the RAG deployment unit.

## Rules

- Fixture-first: every demo scenario works with zero external API calls.
- Live providers are additive fallbacks — never block `/healthz` or CI.
- Secrets only via environment variables; never hardcoded model keys.
- ADR: [`../adr/0002-model-memory-db.md`](../adr/0002-model-memory-db.md).

Architecture: [`../ARCHITECTURE.md`](../ARCHITECTURE.md) §6.
