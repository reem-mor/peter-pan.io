---
name: aws-deployment
description: Use for any AWS work — EC2, CloudFormation, security groups, deployment verification, or managing cloud state from Cursor/Claude Code.
---

# AWS Deployment — PETER PAN

Locked: single EC2 t3.large, docker-compose, CloudFormation. No Kubernetes,
no multi-node, no Terraform (two-week constraint decision — do not reopen).

## Audit-first rule for ANY aws CLI call
Read before write, always. Before any mutating command
(`create-*`, `run-instances`, `terminate-*`, `update-stack`):
1. Run the corresponding `describe-*` and show current state.
2. State the exact change and blast radius in one sentence.
3. Wait for approval. Destructive ops (terminate, delete-stack) additionally
   require the instance-id/stack-name to be echoed back by the user.

## Stack shape (CloudFormation)
- One template: EC2 t3.large + security group + (optional) Elastic IP.
- Security group: inbound ONLY from the n8n cloud egress IPs and the dev
  machine IP, on the specific service ports + 3000 (Grafana). NEVER 0.0.0.0/0.
  Verify after every stack update:
  `aws ec2 describe-security-groups --group-ids <sg> --query "SecurityGroups[].IpPermissions"`.
- Tags on everything: `project=peter-pan`, `env=demo` — cost tracking and
  safe bulk-teardown.

## Deploy procedure
1. `git pull` on the instance (or scp the compose bundle).
2. `docker compose pull && docker compose up -d`.
3. Run the 7/7 verification script; paste its output into the deployment log.
4. Update the EC2-status sentence in the docs (ARCHITECTURE.md et al.) —
   it must always reflect reality (running/stopped, last verified date).

## Cost & hygiene
- The demo instance is STOPPED whenever not actively used — a stopped t3.large
  costs only EBS. Set a reminder habit: verify → record → stop.
- Secrets: instance-side `.env` only, from the committed template. Never in
  user-data, never in the CFN template, never in logs.
- `git log --all --oneline -- "**/kaggle.json"` stays empty forever; extend
  the same check to any new credential filename before first commit.

## Managing from Cursor / Claude Code
- All AWS interaction goes through the CLI in the agent terminal — auditable,
  copy-pastable into deployment notes. No console-clicking that leaves no trail.
- Region and profile pinned in env (`AWS_PROFILE`, `AWS_REGION`) — commands
  never carry ad-hoc `--region` overrides that hide which account they hit.
