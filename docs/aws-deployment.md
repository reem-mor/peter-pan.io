# AWS Deployment — PETER PAN

Demo-scale EC2 deployment. **Synthetic data only.** Do not expose service ports to `0.0.0.0/0`.

## Instance sizing

| Mode | Type | When |
|------|------|------|
| Fixture demo (default) | `t3.large` | Stage A — TF-IDF/Chroma retrieval, no GGUF |
| GGUF inference | `t3.xlarge`+ | After measuring RSS with 7B Q4_K_M model |

## Provision (CloudFormation)

```bash
aws cloudformation deploy \
  --template-file infra/aws/template.yaml \
  --stack-name peter-pan-demo \
  --parameter-overrides InstanceType=t3.large AllowedIngressCidr=<YOUR_IP>/32 EnableBedrock=false \
  --capabilities CAPABILITY_NAMED_IAM
```

Validate template locally:

```powershell
pip install cfn-lint
cfn-lint infra/aws/template.yaml
```

## Deploy application

From Windows (PowerShell):

```powershell
.\scripts\deploy_ec2.ps1 -Host <EC2_PUBLIC_IP> -KeyPath <path-to.pem>
```

Or use `scripts/provision_ec2.sh` + `scripts/remote_deploy_ec2.sh` from bash.

Compose override: `docker-compose.ec2.yml` publishes ports and mounts `/home/ubuntu/models` read-only into RAG.

## Post-deploy checks

```powershell
.\.venv\Scripts\python.exe scripts\test_ec2_public_health.py --host <EC2_IP>
```

Expected: 10/10 services + Grafana healthy.

## n8n on EC2

n8n runs **on the same instance**. Service URLs in compose use Docker internal hostnames (`http://rag:8000`, etc.) — no localhost substitution needed for n8n→service calls.

For external WebUI pointing at EC2 n8n:

```
PETER_UI_N8N_WEBHOOK_URL=http://<EC2_IP>:5678/webhook/peter-signal
```

## Persistent storage

| Data | Path |
|------|------|
| ChromaDB | Docker volume `rag-chroma` → `/data/chroma` |
| GGUF models | `/home/ubuntu/models/` (EBS) |
| Tools audit | `tools-audit` volume |
| n8n state | `n8n-data` volume |

## Enable GGUF (optional Session D)

1. Download Q4_K_M GGUF to `/home/ubuntu/models/`
2. Set `GGUF_MODEL_PATH` in instance `.env`
3. Rebuild RAG image with `llama-cpp-python`
4. `scripts/enable_gguf_ec2.sh` or manual restart
5. `scripts/smoke_rag.py`

## Security

- Security group: **only** `/32` CIDRs (dev IP + n8n egress if external)
- No `0.0.0.0/0` on application ports
- Secrets via `.env` on instance or SSM — never in git
- Containers run non-root

Verified deployment (2026-07-13): `18.234.123.139`, SG `sg-01c3120dcf290c20c`, E2E 7/7.

## Teardown

```bash
aws cloudformation delete-stack --stack-name peter-pan-demo
```

See also: [infra/aws/README.md](../infra/aws/README.md)
