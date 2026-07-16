# Fixture LLM Service

> 35 nodes · cohesion 0.14

## Key Concepts

- **app.py** (26 connections) — `services/fixture-llm/fixture_llm/app.py`
- **ChatMessage** (16 connections) — `services/fixture-llm/fixture_llm/app.py`
- **chat_completions()** (9 connections) — `services/fixture-llm/fixture_llm/app.py`
- **Any** (9 connections)
- **responses()** (8 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_response_for_task()** (7 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_next_agent_tool()** (6 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_tool_grounded_report()** (6 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_agent_evidence()** (5 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_detect_task()** (5 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_parse_tool_result()** (5 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_predictor_policy()** (5 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_responses_messages()** (5 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_synthesis_response()** (5 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_commander_evidence()** (4 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_fixture_id()** (4 connections) — `services/fixture-llm/fixture_llm/app.py`
- **list_models()** (4 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_require_token()** (4 connections) — `services/fixture-llm/fixture_llm/app.py`
- **ResponsesRequest** (4 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_agent_sequence()** (3 connections) — `services/fixture-llm/fixture_llm/app.py`
- **ChatCompletionRequest** (3 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_extract_response()** (3 connections) — `services/fixture-llm/fixture_llm/app.py`
- **BaseModel** (3 connections)
- **_response_input_text()** (3 connections) — `services/fixture-llm/fixture_llm/app.py`
- **_tool_message_name()** (3 connections) — `services/fixture-llm/fixture_llm/app.py`
- *... and 10 more nodes in this community*

## Relationships

- [Escalation Service](Escalation_Service.md) (1 shared connections)

## Source Files

- `docs/audits/2026-07-10-end-to-end-audit.md`
- `docs/presentation/RUBRIC-MAP.md`
- `evaluation/run_e2e.py`
- `infra/aws/template.yaml`
- `services/fixture-llm/fixture_llm/app.py`

## Audit Trail

- EXTRACTED: 164 (97%)
- INFERRED: 5 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*