# AWS course coverage from PITER AiOps

This repo is the **Bedrock capstone** for the AWS AI Engineering course. Use it as your primary workspace for cloud app deployment topics that overlap with PITER; use the sections below for topics **not** built into the main application.

Validation results (2026-07-05): [`evaluation/aws_validation_results.md`](../evaluation/aws_validation_results.md).

## What you can do from `c:\dev\peter-pan.io`

| Course topic | Covered here? | Entry point |
|--------------|---------------|-------------|
| **Bedrock** (Agent, KB, RAG) | Yes — core | `.env`, `scripts/verify_credentials.py`, SPA **AWS / Bedrock** page |
| **S3** | Yes | `scripts/kb_live.py`, `scripts/sync_knowledge_base.py`, upload panel |
| **Lambda** | Yes | `action_groups/`, `scripts/aws_deploy_fix.ps1` |
| **IAM** | Partial | `infra/app_role_policy.json`, `infra/iam_policy_least_privilege.md` |
| **CloudWatch** | Partial | Lambda log checks in `scripts/verify_aws_readiness.py` |
| **EC2** | Partial (deploy only) | `scripts/deploy-ec2-ssm.ps1`, `docs/ec2_deployment.md` |
| **VPC** | Partial (SG/subnet in EC2 docs) | `docs/ec2_deployment.md` |
| **SES / SNS** | Bonus (escalation preview) | `app/services/notification_dispatch.py` |

## Course gaps — not in the main app

These syllabus items require **AWS Console**, **CLI**, or the **minimal lab scripts** under [`scripts/labs/`](labs/):

| Service | In PITER app? | Where to practice |
|---------|---------------|-------------------|
| **RDS** | No | AWS Console RDS lab, or `aws rds describe-db-instances` |
| **Transcribe** | No | [`scripts/labs/transcribe_lab.py`](labs/transcribe_lab.py) |
| **Polly** | No | [`scripts/labs/polly_lab.py`](labs/polly_lab.py) |
| **Textract** | No | [`scripts/labs/textract_lab.py`](labs/textract_lab.py) |
| **Rekognition** | No | [`scripts/labs/rekognition_lab.py`](labs/rekognition_lab.py) |
| **Comprehend** | No | [`scripts/labs/comprehend_lab.py`](labs/comprehend_lab.py) |

Run all AI service labs (dry-run / safe defaults):

```powershell
cd C:\dev\peter-pan.io
$env:AWS_PROFILE = "reemmor"
.\.venv\Scripts\python.exe scripts\labs\run_all_labs.py
```

## EC2 public demo

No instance tagged `piter-aiops-demo` was running on 2026-07-05. To ship a public demo:

1. Launch EC2 per [`ec2_deployment.md`](ec2_deployment.md)
2. Set `PITER_EC2_INSTANCE_ID` and `PITER_ARTIFACTS_BUCKET` in your shell or `.env`
3. `.\scripts\deploy-ec2-ssm.ps1 -Verify`

Until an instance exists, local demo at `http://127.0.0.1:8080` is sufficient for Bedrock coursework.

## Portfolio narrative

- **Strong in this repo:** Bedrock Agent + KB RAG, S3 corpus pipeline, Lambda action groups, Flask/React ops console, IAM least-privilege intent.
- **Acknowledge separately:** RDS; classic AI services (Transcribe, Polly, Textract, Rekognition, Comprehend) — use `scripts/labs/` or original course modules.

## Quick validation (after `.env` is populated)

```powershell
$env:AWS_PROFILE = "reemmor"
.\.venv\Scripts\python.exe scripts\verify_credentials.py
.\.venv\Scripts\python.exe scripts\agent_smoke_test.py
.\scripts\run-local.ps1
# optional UI: cd frontend && npm run dev  →  http://localhost:5173
```
