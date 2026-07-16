# AWS Deployment — PETER PAN

**Canonical operator guide:** [`infra/aws/README.md`](../infra/aws/README.md)
(CloudFormation sizing, deploy, validate, teardown, security notes).

Application deploy on a provisioned instance (Windows):

```powershell
.\scripts\deploy_ec2.ps1 -IP <EC2_PUBLIC_IP> -KeyFile <path-to.pem>
```

Bash alternatives: `scripts/provision_ec2.sh`, `scripts/deploy_ec2.sh`,
`scripts/remote_deploy_ec2.sh`. Compose override: `docker-compose.ec2.yml`
(publishes service ports; SG is the gate). Skill: `.claude/skills/ec2-deploy/`.

Post-deploy:

```powershell
.\.venv\Scripts\python.exe scripts\test_ec2_public_health.py --host <EC2_IP>
```

n8n runs on-instance; WebUI webhook example:
`PETER_UI_N8N_WEBHOOK_URL=http://<EC2_IP>:5678/webhook/peter-signal`.

Verified demo window (2026-07-13): `<demo-public-ip>`, SG `<demo-sg-id>`, E2E 7/7 —
placeholders only; never commit live IPs.
