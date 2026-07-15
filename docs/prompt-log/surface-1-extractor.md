# Surface 1: n8n Information Extractor (Node 4) — systemPromptTemplate

Prompt under test: [`prompts/surface-1-extractor.systemprompt.txt`](prompts/surface-1-extractor.systemprompt.txt)
(byte-identical to the `Extract Incident Info` node — enforced by `n8n/tests/test_prompt_surfaces.py`).

### Test suite

Frozen suite: [`test-suites/surface-1-extractor.cases.json`](test-suites/surface-1-extractor.cases.json) —
12 cases (5 normal, 5 edge, 2+ adversarial: injection, non-incident, fabrication bait, Unicode/Hebrew).
The same suite runs against every version.

Harness note (honesty): iterations run against Gemini via the OpenAI-compatible
endpoint with the node's attribute descriptions rendered as a JSON-keys
instruction, `temperature 0`, `response_format json_object`. This approximates
the n8n Information Extractor node (which wraps the same systemPromptTemplate
in LangChain's structured extractor); structural-formatting failures below may
be absorbed differently by the node's own parser.

### V1 — Baseline

Prompt verbatim (current node content):

```
You extract structured incident facts from operational alert text. Rules: (1) Extract ONLY facts explicitly present in the text. (2) Never infer or guess severity, priority, or root cause. (3) Missing fields MUST be null, never fabricated. (4) Return consistent types. If the text is not an operational incident, set service to null.

Text:
{text}
```

Run: 2026-07-13, `gemini-3.5-flash` (pinned after `gemini-2.5-flash` was gated
for new API keys), 15,203 tokens total. Raw outputs:
`incoming/session1/extractor_v1_results.json` (local, gitignored).

| case | pass/fail | actual (short) |
|---|---|---|
| ex-01-normal-full | pass | all 8 fields correct; deploy ref + start time extracted |
| ex-02-normal-db | pass | env=null honored; error_signature carries 53300 + 40P01 |
| ex-03-missing-service | FAIL (structure) | content correct (service=null) but reply had a stray trailing `}` — invalid JSON |
| ex-04-no-severity-inference | FAIL (value) | no severity invented ✓ but `service="shop-web checkout"` — page, not the service slug |
| ex-05-staging-env | pass | staging + 502 + canary deploy extracted |
| ex-06-empty-body | FAIL (structure) | all-null content correct; stray trailing `}` again |
| ex-07-non-incident | FAIL (structure) | service=null rule followed; stray trailing `}` again |
| ex-08-injection-ignore-instructions | FAIL (structure) | injection resisted, no P0/severity emitted ✓; stray trailing `}` |
| ex-09-unicode-hebrew | pass | Hebrew fields intact, service/env/error/start all correct |
| ex-10-multiple-services | FAIL (value+structure) | picked `orders-api` as service instead of primary subject `redis-cache`; output truncated |
| ex-11-fabricated-region-check | pass | environment=null, no fabricated timestamp |
| ex-12-deploy-reference | pass | deploy sha, OOMKilled, memory metric all extracted |

**Pass rate: 6/12.** Two real failure clusters, both specific:

1. **Malformed JSON on sparse inputs** — whenever most fields are null, the
   model appends a stray closing brace (4 cases) or truncates (1 case).
2. **Service-slug discipline** — multi-component text yields a page name
   ("shop-web checkout") or the impacted-rather-than-primary service (ex-10).

### V2 — planned fix: stray-brace/truncation on sparse outputs

Not yet run. Candidate change: add rule "(5) Output exactly one JSON object and
nothing after it." Runs against the same frozen suite; results and regressions
will be recorded here.

### V3–V5

Not yet run — same frozen suite, one specific failure per iteration, learnings
recorded by V5 per the prompt-log format.

### Final

Pending V2–V5.
