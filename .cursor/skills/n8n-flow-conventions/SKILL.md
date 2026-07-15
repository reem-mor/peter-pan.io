---
name: n8n-flow-conventions
description: Use for any n8n work — node configuration, expressions, the 8-node triage flow, webhook payloads, parallel EC2 calls and their merge, or the flow-export deliverable.
---

# n8n Flow Conventions — PETER PAN Triage Pipeline

The flow is the conductor: it does no AI itself, it decides who talks to whom
and in what order. 8 nodes, mapped 1:1 to the course spec. Before editing the
flow, export the current version — every structural change gets a fresh export
committed alongside it.

## The 8 nodes (fixed — do not add/remove without explicit approval)
1. **Webhook** — POST from Streamlit. Respond mode: `responseNode`
   (Respond to Webhook nodes return the TriageReport / reject / suppress
   payload; immediate-respond returns empty and the UI shows nothing).
2. **Guardrails Input** — HTTP Request → EC2 `/check/input`.
3. **IF** — condition on `{{ $json.passed }}` (boolean true). Fail branch →
   Reject node returning `{passed: false, flags, reason}` verbatim to the UI.
4. **Information Extractor** (Gemini LM) — prompt surface #1. The
   systemPromptTemplate lives in a versioned file; paste into the node, never
   author it only inside n8n (the prompt log needs git history).
5. **AI Agent** (GPT-4o/Gemini) — prompt surface #2. Tools = HTTP calls to
   RAG, Predictor, LangGraph.
6. **LLM Chain** — synthesizes the incident brief. Always paired with a
   Structured Output Parser node; the schema mirrors the brief model in
   `contracts.py`.
7. **Guardrails Output** — HTTP Request → `/check/output`. Fail → flag for
   review branch, never return the brief as-is.
8. **Router (Switch)** — 3-way on the routing category derived from
   `{{ $json.incident_class }}`. The 6→3 mapping table lives HERE and only
   here; services return the raw class.

## Expression gotchas (the usual failure points)
- `{{ $json.field }}` reads the CURRENT input item. To reach an earlier
  node's output after merges: `{{ $('Node Name').item.json.field }}` — exact
  node name, case-sensitive.
- HTTP Request nodes: body type JSON, `Content-Type: application/json` set
  explicitly. n8n silently sends form-encoded otherwise and FastAPI returns
  422 — if you see 422 from a service, check this FIRST.
- Timeouts: set per HTTP node (30s services, 60s LLM nodes). Default is
  effectively infinite and hangs the whole execution.
- Booleans in IF nodes: compare as boolean, not string — `"false"` is truthy.

## Parallel calls and the merge (the dashed lines)
Node 5's tool calls are agent-managed (the Agent node handles them
internally). If the flow ALSO has direct parallel HTTP branches, they must
reconverge through a **Merge node (mode: Combine, by position)** before the
LLM Chain — the Chain must see ONE item containing rag/predictor/langgraph
keys. Two items in = two briefs out = duplicated output in the UI.

## Webhook payload contract (UI → flow)
```json
{ "description": "...", "service": "...", "severity_hint": "P1|P2|P3|P4|null",
  "context": "...", "submitted_by": "..." }
```
Change it in one place = change it in three: Streamlit POST, this skill,
the Extractor prompt's input description.

## Environment & deliverable
- Service base URLs come from n8n variables/credentials — never hardcode the
  EC2 IP in nodes (it changes on stop/start without an Elastic IP).
- Deliverable: flow exported as importable JSON, committed at
  `n8n/peter-flow.json`. Strip credentials before commit (export never
  includes secrets, but verify — grep the JSON for the EC2 IP and tokens).
- Test the flow with `curl` against the webhook BEFORE testing via the UI —
  isolates flow bugs from UI bugs.
