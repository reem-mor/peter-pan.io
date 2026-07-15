# Surface 2: n8n AI Agent — Incident Commander (Node 5)

Prompts under test:
- [`prompts/surface-2-agent.systemmessage.txt`](prompts/surface-2-agent.systemmessage.txt) — agent system message
- [`prompts/surface-2-agent.tools.json`](prompts/surface-2-agent.tools.json) — the four tool descriptions

Both byte-identical to the live nodes (`Incident Commander`, `Predictor Tool`,
`RAG Query Tool`, `LangGraph Agent Tool`, `Service Context Tool`) — enforced by
`n8n/tests/test_prompt_surfaces.py`.

### Test suite

Frozen suite: [`test-suites/surface-2-agent.cases.json`](test-suites/surface-2-agent.cases.json) —
12 cases covering tool-order discipline (Predictor first, normal-stops-early,
single-domain vs cross-domain routing), verbatim tool-result copying, and
adversarial cases (self-diagnosed alerts, invented citations/owners, prompt
injection inside incident bodies).

### V1 — Baseline

Prompt verbatim (current node systemMessage):

```
You are a senior incident commander for a production SRE team. Always call Predictor Tool first. If its incident_class is normal, stop and return that exact predictor result. For a non-normal single-domain incident, then call RAG Query Tool and Service Context Tool; do not call LangGraph. For a complex cross-domain incident, call LangGraph Agent Tool after Predictor and do not call RAG directly because LangGraph owns retrieval. Return one JSON object containing the exact tool results under predictor, rag, service_context, or langgraph. Never invent incident_class, severity, routing category, owners, escalation paths, citations, runbook IDs, or root causes.
```

**Execution status (honesty): live baseline BLOCKED → Layer 4.** Tool-selection
behavior can only be measured against a real agent-capable provider; the Stage A
Commander runs on the deterministic FixtureLLM, whose tool sequence is scripted
(`_agent_sequence` in `services/fixture-llm`), so running this suite against the
fixture would measure the fixture, not the prompt. What IS verified in Stage A:
the E2E fixture path exercises ag-01/02/03/04/05/12 mechanically (see
`evaluation/run_e2e.py` results), and the flow's static tests pin the
"do not call RAG directly" instruction (`test_commander_prompt_prevents_duplicate_rag`).

### V2–V5

Not yet run — will execute once a live agent provider is bound (Session 3,
Layer 4). Same frozen suite, per-version results tables.

### Final

Pending live-provider iterations.
