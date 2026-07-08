# AWS validation results — 2026-07-05

Run from `c:\dev\peter-pan.io` with profile `reemmor` and populated `.env`.

## verify_credentials.py

**PASS** — Account `329597159579`, agent alias PREPARED, KB ACTIVE.

## verify_aws_readiness.py

**12 PASS, 3 FAIL, 6 WARN** (exit 1 — cost section log retention only)

| Section | Result | Notes |
|---------|--------|-------|
| Functional (agent, KB, Lambdas, models) | PASS | All core wiring OK |
| Security (S3 hardening) | WARN | Placeholder bucket names in script defaults; real bucket `reem-amdocs-ai-artifacts-3331` not checked |
| Cost (log retention) | 3 FAIL | `piter-recent-deployments`, `piter-service-context`, `piter-similar-incidents` — retention never expire |
| EC2 | SKIP | No demo instance running |

Fix log retention (optional):

```powershell
aws logs put-retention-policy --log-group-name /aws/lambda/piter-recent-deployments --retention-in-days 14
aws logs put-retention-policy --log-group-name /aws/lambda/piter-service-context --retention-in-days 14
aws logs put-retention-policy --log-group-name /aws/lambda/piter-similar-incidents --retention-in-days 14
```

## agent_smoke_test.py

**PASS** — 6/6 questions. See [`agent_smoke_results.md`](agent_smoke_results.md).

## Local app demo (API)

**PASS** — Backend on `http://127.0.0.1:8080` with profile `reemmor`.

| Check | Result |
|-------|--------|
| `/api/health?deep=1` | `status: ok`, `bedrock: configured`, `s3: configured` |
| `/api/bootstrap` | `use_bedrock: true`, `kb_id: RBTJM6NIG9`, `rag_backend: agent` |
| `/api/tools/status` | All 4 action groups `ready` |
| `POST /api/chat` | Grounded answer with tool `get_recent_deployments` |

Bedrock status page data sources: `fetchHealth(deep)` + `fetchBootstrap()` — same endpoints above.

## AI service labs (`scripts/labs/`)

**PASS** — 5/5 on 2026-07-05 (profile `reemmor`, region `us-east-1`):

| Lab | Result |
|-----|--------|
| Transcribe | OK — API reachable |
| Polly | OK — 15 en-US voices |
| Textract | OK — list adapters |
| Rekognition | OK — 0 collections |
| Comprehend | OK — detect_dominant_language |

Run: `.\.venv\Scripts\python.exe scripts\labs\run_all_labs.py --profile reemmor`

## EC2 public demo

**SKIP** — No instance tagged `piter-aiops-demo` in account `329597159579` (2026-07-05).

To deploy when needed:

```powershell
$env:PITER_EC2_INSTANCE_ID = "i-xxxxxxxx"
$env:PITER_ARTIFACTS_BUCKET = "reem-amdocs-ai-artifacts-3331"
.\scripts\deploy-ec2-ssm.ps1 -SkipDockerBuild -SkipS3Upload -Verify
```

Launch checklist: [`docs/ec2_deployment.md`](../docs/ec2_deployment.md).
