# PETER PAN — Documentation Reconciliation & Fix Report

A single, ranked list of every **conflict, fix, and deletion** across the project docs,
checked against the teacher's guideline and the source-of-truth diagrams
(`peter-pan-system.mmd`, `peter-pan-n8n-flow.mmd`). Work top-to-bottom; each item says
**where**, **why**, and **the exact fix** (with before/after where useful).

Severity: 🔴 can hurt you in front of the teacher/employer · 🟠 real drift, fix before submit · 🟡 tidy-up.

---

## 0. How to use this

Drive Cursor one item at a time: *"Read `docs/DOCS-RECONCILIATION.md` item F1, then apply
the fix. Show me the diff, don't commit."* Do the 🔴 items first, then the four decisions
in Part 4, then the rest. Nothing here touches product code — it's docs + one contract addition.

---

## 1. Severity summary

| # | Item | Sev | Type |
|---|---|---|---|
| F1 | EC2 status contradicts itself (planned vs passed-on-EC2) | 🔴 | Fix + decide |
| D1 | `PROJECT_PLAN_v2.md` — retire (P5, wrong categories, out-of-scope Twilio/HITL) | 🔴 | Delete |
| D2 | `BUILD_PLAN_v2.md` — retire (introduces out-of-scope Twilio, drops scope guards) | 🟠 | Delete |
| D3 | `ARCHITECTURE_v2.md` vs `ARCHITECTURE.md` — one canonical file | 🟠 | Delete/merge |
| F2 | Guardrail output schema has 3 shapes; not pinned in `contracts.py` | 🟠 | Fix + decide |
| F3 | "category" overloaded: predictor 6-class vs TriageReport 3-class | 🟠 | Fix + decide |
| F4 | LangGraph tools wrong in `MASTER-CHECKLIST` (says RAG+Predictor) | 🟠 | Fix |
| F5 | Node 5 tool count: diagram=4, prose docs=3 | 🟡 | Fix |
| F6 | `image-analyzer` in diagram but missing from ADR 0003 | 🟡 | Fix |
| F7 | Corpus size: ≥20 / ≥30 / ≥55 across docs | 🟡 | Fix |
| I1 | `DEMO-SCRIPT.md` missing 3 of 4 required demo scenes | 🟠 | Improve |
| I2 | `/analyse` vs `/analyze` spelling split | 🟡 | Improve |
| I3 | Python 3.14.5 local vs 3.12 target | 🟡 | Improve |

---

## 2. DELETE — duplicate / superseded files

The pattern across all three pairs: **the non-`_v2` (v1) file is the better, canonical one.**
The `_v2` files are either simplified rewrites that lost rigor or introduced out-of-scope scope creep.

### D1 🔴 Delete `PROJECT_PLAN_v2.md` — keep `PROJECT-PLAN.md`
`PROJECT_PLAN_v2` conflicts with your frozen contracts and your own source-of-truth diagram:

| `PROJECT_PLAN_v2` says | Reality (contract / diagram) |
|---|---|
| Severity **"P5–P1"** | `contracts.py`: `p_level: Literal["P1","P2","P3","P4"]` — **there is no P5** |
| Categories **"CPU, Memory, DB Lock, Network"** (4) | crosswalk: **6** classes; router: **3** (infra/db/app) — neither is this 4-set |
| **Twilio** voice calls, Slack **HITL** buttons | Not in `peter-pan-system.mmd`. BUILD_PLAN's own rule: *"anything not in the diagrams is out of scope."* Twilio is out of scope by your own rule |
| Datasets: **telco / gaming / SaaS** | BUILD_PLAN v1 explicitly *replaces* that "three-way mismatch" with `shop-web`/`orders-api`/PostgreSQL |
| DoD: **"All 4 extensions implemented"** | Extensions are extra-credit, post-`v0.2`, *"none may delay a graded component"* |

`PROJECT-PLAN.md` (v1) is the honest rubric crosswalk with the decision log, consistent with
contracts and ADRs. Keep it; delete v2.

### D2 🟠 Delete `BUILD_PLAN_v2.md` — keep `BUILD_PLAN.md`
`BUILD_PLAN.md` (v1) is far superior: it has the contract seed, packaging rule, component→node
inventory, risk register, effort-honesty section, and the resolved-conflicts log. `BUILD_PLAN_v2`
is a simplified rewrite that **adds out-of-scope Twilio** ("Configure Twilio for voice calls on
P1s") and **drops the scope guards**. Keep v1, delete v2.

### D3 🟠 Collapse `ARCHITECTURE_v2.md` into `ARCHITECTURE.md`
These two are **byte-identical except one row** — the EC2 status (see F1). Resolve F1 first,
then keep **one** file (`ARCHITECTURE.md`) with the correct EC2 row and delete the other.
Two-of-each is guaranteed drift; your `CLAUDE.md` links point at the non-`_v2` name.

---

## 3. FIX — conflicts, ranked

### F1 🔴 EC2 deployment status contradicts itself
The single highest-risk item, because it can blow up live in a presentation.

| Doc | Says |
|---|---|
| `ARCHITECTURE.md` | EC2 = **"Planned (Stage C / demo)"** |
| `ARCHITECTURE_v2.md` | EC2 = **"Implemented (demo)… full n8n-path E2E passed 7/7 on EC2 2026-07-11"** |
| `RUBRIC-MAP.md`, `DEMO-SCRIPT.md`, audit | EC2 deploy **"not yet claimable" / "remain planned"**; read-only AWS check found **no instance currently deployed** |

**Likely truth:** you provisioned a demo EC2 (`18.234.123.139` appeared in your `settings.local.json`
`deploy_ec2.sh`/`run_e2e_ec2.sh`), passed 7/7 on it, then **stopped/tore it down** to cap cost
(matching your "stop between sessions" scope). If so, every doc is half-right and collectively
contradictory.

**Fix — pick ONE precise present-tense wording and put it in every doc.** Recommended:

> **AWS EC2 deployment — Verified (demo), not currently running.** Deploy tooling
> (`provision_ec2.sh`, `deploy_ec2.sh`, `docker-compose.ec2.yml`) exists; a demo instance was
> provisioned and passed the full n8n-path E2E 7/7 on 2026-07-11, then stopped to cap cost.
> No instance is currently running; re-provision is one script.

Then update `ARCHITECTURE.md`, `RUBRIC-MAP.md` ("Not yet claimable" → move EC2 to "Demonstrated,
instance stopped"), `DEMO-SCRIPT.md` ("does not claim… AWS deployment" → "EC2 verified, instance
stopped for cost"), and the audit. **Verify first:** run `aws ec2 describe-instances` to confirm
today's actual state before choosing wording. Never present both *"no live provisioning"* and
*"passed on EC2"* in the same submission.

### F2 🟠 Guardrail output schema — three shapes, none frozen
`contracts.py` defines `Signal`/`Incident`/`IncidentContext`/`TriageReport` but **not** the
guardrail response — so it drifted into three shapes:

| Source | Shape |
|---|---|
| Guideline | `{pass, reason, safe_text}` |
| `PROJECT-PLAN.md` v1 §5.3.3 | `{pass, flags, reason}` |
| `MASTER-CHECKLIST.md` / skill | `{valid, reason}` |

**Fix:** pick one and **add it to `contracts.py`** so the contract-identity test enforces it.
Recommended `{pass, flags, reason}` — it aligns with the existing `TriageReport.guardrail_flags`.

```python
# add to docs/contracts/contracts.py
class GuardrailResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    passed: bool                                   # `pass` is a Python keyword — use `passed`
    flags: list[str] = Field(default_factory=list) # non-empty → review queue
    reason: str = Field(default="", max_length=500)
```
Then align `MASTER-CHECKLIST` §5.3 (drop `{valid, reason}`), the `guardrails-testing` skill, and
`PROJECT-PLAN` §5.3.3 to this one shape. (Note the `pass`→`passed` rename — `pass` is reserved in Python.)

### F3 🟠 "category" means two different things
- `TriageReport.category` = `Literal["infra","database","application"]` — **3-way routing** (drives node 8).
- Predictor `/analyse` output `category` = **6 incident classes** (`cpu_saturation`…`normal`).

Same field name, two taxonomies → confusion and silent bugs.

**Fix (pick one):**
- **(a) Rename the predictor field** to `incident_class` (6 classes), keep `TriageReport.category`
  as the 3-way routing bucket, and document the deterministic map:
  `cpu_saturation|memory_leak → infra` · `db_lock_contention|replication_lag → database` ·
  `error_rate_spike → application` · `normal → suppressed`.
- **(b)** Collapse to the 3 routing classes everywhere and drop the 6-class taxonomy.

Recommend **(a)** — the 6-class predictor is your declared deviation (maps 1:1 to the guideline's
6 room types) and is worth keeping for the Image-Analyser rubric line. Add the mapping table to
`ARCHITECTURE.md` and fix the `incident-triage` skill (which currently lists the 6 as "the category").

### F4 🟠 LangGraph tools are wrong in `MASTER-CHECKLIST`
`MASTER-CHECKLIST` §5.4 says LangGraph = "planner → specialists (**RAG+Predictor**)". But
`PROJECT-PLAN` v1 §5.3.4 and ADR 0003 say LangGraph calls **RAG + Tools API** (n8n owns the
separate Predictor call, and *"when LangGraph is active, RAG is owned by LangGraph"*).

**Fix:** correct `MASTER-CHECKLIST` §5.4 to "planner → specialists (**RAG + Tools API**) →
synthesiser; Predictor is a separate n8n commander tool." (This is my error in the checklist I
generated — owning it.)

### F5 🟡 Node 5 tool count: 4 vs 3
`peter-pan-n8n-flow.mmd` (source of truth) shows node 5 (AGT) calling **four** tools:
T1 RAG, T2 Predictor, T3 LangGraph, **T4 Tools API (`/tools/service_context`)**. But
`ARCHITECTURE.md`'s runtime-flow ASCII and `MASTER-CHECKLIST` §4 show only **three** (omit Tools API).

**Fix:** update the ASCII flow in `ARCHITECTURE.md` and `MASTER-CHECKLIST` §4 node 5 to list all
four tool calls, matching the diagram.

### F6 🟡 `image-analyzer` is in the diagram but missing from ADR 0003
Resolved by the diagram: `peter-pan-system.mmd` shows **"Image Analyzer Seam — ResNet scaffold ·
not flow-integrated."** So it's a *declared* vision-fallback seam, **not** cruft — good. But
`ADR 0003`'s service inventory lists only six units and doesn't mention it, and ARCHITECTURE calls
the repo "nine units."

**Fix:** add one line to `ADR 0003` declaring `image-analyzer` as the **non-graded vision-fallback
seam** (the documented fallback for D-2 if a literal image model is ever required). Then the counts
reconcile cleanly: *4 graded + 2 support + 3 seams (image-analyzer, fixture-llm, integration-stubs) = 9 dirs.*

### F7 🟡 Corpus size inconsistent
≥20 (guideline min) · ≥30 (`PROJECT_PLAN_v2`, being deleted) · ≥55 (everywhere else). Also
`MASTER-CHECKLIST` §5.1 says both "≥55" and "≥20-doc corpus seeded" in the same section.

**Fix:** standardize on **≥55** (25 runbooks + 30 incidents). Update `MASTER-CHECKLIST` §5.1's
"≥20-doc corpus seeded" checkbox to "≥55-doc corpus seeded."

---

## 4. IMPROVE

### I1 🟠 `DEMO-SCRIPT.md` is missing 3 of the 4 required demo scenes
The guideline mandates exactly four demo scenes: **successful E2E**, **input-guardrail fail**,
**output-guardrail fail**, **Ollama assistant exchange**. `DEMO-SCRIPT.md` scripts the successful
path + architecture + evidence, but not the two guardrail-failure scenes or the Ollama chat as
distinct moments. Good news: `PROJECT-PLAN.md` §9 already has the correct four-scene storyboard.

**Fix:** port that four-scene storyboard into `DEMO-SCRIPT.md` as explicit timestamped segments.
Narrate the two failure scenes like an SRE incident (detection → log trail → human handoff).

### I2 🟡 `/analyse` vs `/analyze`
Predictor uses `/analyse` (British); image-analyzer seam uses `/analyze` (American). The guideline
uses `/analyse`. Keep `/analyse` for the graded predictor; leave the seam as-is or align — just
don't let a doc claim the predictor is at `/analyze`.

### I3 🟡 Python version
Audit notes local `3.14.5` vs CI/target `3.12` (deprecation warnings from Starlette/LangGraph).
Keep **3.12** pinned as target; consider matching locally so the demo run is warning-free.

---

## 5. Decisions you must make (before the fix pass)

Four choices only you can make — everything above depends on them:

1. **EC2 wording (F1):** confirm today's actual state (`aws ec2 describe-instances`) and pick the
   present-tense sentence. → drives ARCHITECTURE/RUBRIC-MAP/DEMO-SCRIPT/audit edits.
2. **Guardrail schema (F2):** `{pass, flags, reason}` (recommended) vs alternatives. → drives
   `contracts.py` + 3 docs + 1 skill.
3. **Category naming (F3):** rename predictor field to `incident_class` (recommended) vs collapse
   to 3 classes. → drives ARCHITECTURE + `incident-triage` skill.
4. **image-analyzer (F6):** declare as vision-fallback seam in ADR 0003 (recommended) vs remove.

---

## 6. File-by-file verdict (navigation)

| File | Verdict |
|---|---|
| `docs/contracts/contracts.py` | ✅ Keep. **Add** `GuardrailResult` (F2). |
| `docs/contracts/export_json_schema.py` | ✅ Keep. Add `GuardrailResult` to `MODELS` if you freeze it. |
| `docs/llm_client.py` | ✅ Keep — clean. |
| `docs/peter-pan-system.mmd` | ✅ Keep — source of truth. |
| `docs/peter-pan-n8n-flow.mmd` | ✅ Keep — source of truth (has the 4-tool node 5). |
| `docs/ARCHITECTURE.md` | ✅ Keep — **fix EC2 row (F1), node-5 tools (F5), category map (F3), 6-vs-9 (F6).** |
| `docs/ARCHITECTURE_v2.md` | ❌ Delete after merging its (corrected) EC2 row into ARCHITECTURE.md (D3). |
| `docs/BUILD_PLAN.md` | ✅ Keep — canonical. |
| `docs/BUILD_PLAN_v2.md` | ❌ Delete (D2). |
| `docs/PROJECT-PLAN.md` | ✅ Keep — canonical crosswalk. Align guardrail shape (F2). |
| `docs/PROJECT_PLAN_v2.md` | ❌ Delete (D1). |
| `docs/MASTER-CHECKLIST.md` | ✅ Keep — **fix LangGraph tools (F4), guardrail shape (F2), node-5 (F5), corpus (F7).** |
| `docs/model-memory-db-rationale.md` | ✅ Keep — consistent with ADR 0002. |
| `docs/adr/0002-model-memory-db.md` | ✅ Keep. |
| `docs/adr/0003-system-boundaries.md` | ✅ Keep — **add image-analyzer seam line (F6).** |
| `docs/audits/2026-07-10-end-to-end-audit.md` | ✅ Keep — update EC2 wording (F1). |
| `docs/AGENT-TOOLING.md` | ✅ Keep — clean. |
| `docs/DEMO-SCRIPT.md` | ✅ Keep — **add the 3 missing scenes (I1).** |
| `docs/RUBRIC-MAP.md` | ✅ Keep — update EC2 wording (F1). |
| `docs/PRE-PUBLIC-CHECKLIST.md` | ✅ Keep — unrelated (secrets track). |

---

## 7. Recommended execution order

1. **Decide** the four choices in Part 5 (F1 needs `aws ec2 describe-instances`).
2. **Delete** `PROJECT_PLAN_v2.md`, `BUILD_PLAN_v2.md` (D1, D2).
3. **Fix EC2 wording** (F1) across ARCHITECTURE/RUBRIC-MAP/DEMO-SCRIPT/audit, then **collapse**
   ARCHITECTURE_v2 → ARCHITECTURE (D3).
4. **Add `GuardrailResult` to `contracts.py`** (F2), align the 3 docs + skill.
5. **Category rename/map** (F3), fix `incident-triage` skill.
6. **Small fixes:** F4, F5, F6 (ADR line), F7, I1, I2, I3.
7. Re-run `python scripts/run_all_tests.py` + contract-identity test (only F2 touches code, so this
   should stay green after you vendor the new model into services).

Net: your **engineering** is coherent and well-built — the drift is entirely in the **documentation
layer**, concentrated in three deletable `_v2` files and four naming decisions. Clear those and the
docs match the code.
