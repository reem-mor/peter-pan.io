# LLM Client Protocols

> 19 nodes · cohesion 0.22

## Key Concepts

- **llm_client.py** (8 connections) — `docs/llm_client/llm_client.py`
- **build_llm_client()** (7 connections) — `docs/llm_client/llm_client.py`
- **LLMResult** (6 connections) — `docs/llm_client/llm_client.py`
- **Any** (5 connections)
- **TaskKind** (5 connections)
- **BedrockLLMClient** (4 connections) — `docs/llm_client/llm_client.py`
- **.complete()** (4 connections) — `docs/llm_client/llm_client.py`
- **FixtureLLMClient** (4 connections) — `docs/llm_client/llm_client.py`
- **.complete()** (4 connections) — `docs/llm_client/llm_client.py`
- **GeminiLLMClient** (4 connections) — `docs/llm_client/llm_client.py`
- **.complete()** (4 connections) — `docs/llm_client/llm_client.py`
- **LLMClient** (4 connections) — `docs/llm_client/llm_client.py`
- **.complete()** (4 connections) — `docs/llm_client/llm_client.py`
- **OllamaLLMClient** (4 connections) — `docs/llm_client/llm_client.py`
- **.complete()** (4 connections) — `docs/llm_client/llm_client.py`
- **Stage C adapter stub — raises until configured.** (3 connections) — `docs/llm_client/llm_client.py`
- **Protocol** (1 connections)
- **Canonical LLM client seam — vendored into services that need generation.** (1 connections) — `docs/llm_client/llm_client.py`
- **Deterministic canned responses keyed by task.** (1 connections) — `docs/llm_client/llm_client.py`

## Relationships

- [Escalation Service](Escalation_Service.md) (1 shared connections)

## Source Files

- `docs/llm_client/llm_client.py`

## Audit Trail

- EXTRACTED: 76 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*