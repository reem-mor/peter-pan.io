---
name: ec2-deploy
description: Provisions, deploys, and validates the PETER PAN Stage A demo stack on AWS EC2. Use for any EC2 provisioning, stack deployment, redeploy, security-group change, n8n owner recovery, or live E2E validation against the instance.
---

# PETER PAN — EC2 demo deployment

## Invariants

- Security group inbound is ONLY the current dev IP `/32` — never `0.0.0.0/0`.
  `scripts/provision_ec2.sh` revokes any world-open rule it finds.
- n8n runs ON the instance inside the compose network; no external n8n IP rule exists.
- The local `.env` is never transferred. The instance generates its own `.env`
  (mode 600) on first deploy and keeps it across redeploys so n8n keys stay stable.
- Keypair PEM lives at `~/.ssh/peter-pan-key.pem` — never in the repo.
- `fixture-llm` (8010) stays loopback-only on the instance; it is an internal seam.
- Git Bash: every script that passes `/aws/...`-style args must set
  `MSYS_NO_PATHCONV=1` or MSYS mangles them into Windows paths.

## Standard sequence

```bash
bash scripts/provision_ec2.sh                    # idempotent; prints public IP
bash scripts/deploy_ec2.sh [ip]                  # package -> ship -> build -> bootstrap -> on-instance health
python scripts/test_layer3_health.py --base-url http://<ip>   # external /healthz x6
PETER_SERVICES_TOKEN=<instance token> python evaluation/run_e2e.py --entrypoint n8n --base-url http://<ip>
```

The E2E token is the INSTANCE's `PETER_SERVICES_TOKEN`
(`ssh -i ~/.ssh/peter-pan-key.pem ubuntu@<ip> "grep PETER_SERVICES_TOKEN ~/peter-pan/.env"`);
export it into the environment — do not echo it into logs or commit it anywhere.

## Compose files

- `docker-compose.yml` — base; ports bound to `127.0.0.1` (local dev).
- `docker-compose.ec2.yml` — override; publishes 8001-8006, 8020, 5678 (SG is the gate).
  Always pass BOTH files with `-f` on the instance, including for `--profile bootstrap`.

## n8n owner recovery (lost password / lost .env)

The encryption key is recoverable from the volume; the owner password is not:

1. `docker run --rm -v peter-pan_n8n-data:/data alpine cat /data/config`
   → `encryptionKey` (put straight into `.env`; never print in logs).
2. `docker compose exec -T n8n n8n user-management:reset` — clears only the
   owner account; workflows and credentials survive.
3. `docker compose restart n8n`, then re-run the bootstrap profile — it recreates
   the owner from `N8N_OWNER_*` and re-syncs `n8n/peter-flow.json`.

Never fix a lost password by deleting the `n8n-data` volume; that also needs
explicit user approval per repo golden rules.

## Known traps

- Named-volume dirs (e.g. tools-api `/data`) must be owned by uid 10001 in the
  image, or SQLite fails with "unable to open database file" and `/audit` 500s.
- `docker compose exec` under Git Bash converts `/data` → `C:/...`; prefix with
  `MSYS_NO_PATHCONV=1`.
- Teardown (`terminate-instances`, `down -v`) is destructive — requires explicit
  user approval first.

## Audit-first AWS CLI (migrated from aws-deployment)

Before any mutating command (`create-*`, `run-instances`, `terminate-*`, `update-stack`):

1. Run the corresponding `describe-*` and show current state.
2. State the exact change and blast radius in one sentence.
3. Wait for approval. Destructive ops require the instance-id/stack-name echoed back.

Stack shape: CloudFormation only (`infra/aws/template.yaml`) — one EC2 t3.large + SG.
Never `0.0.0.0/0`. Tags: `project=peter-pan`, `env=demo`. Operator SoT:
[`infra/aws/README.md`](../../../infra/aws/README.md). Stop the demo instance when idle
(EBS-only cost). Never put live public IPs or instance IDs into tracked docs.
