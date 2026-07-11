# PETER PAN — AWS demo deployment

Single-VPC, single-EC2 portfolio stack. **Synthetic data only.** Do not expose service ports 8001–8006 publicly.

## Sizing

| Mode | Instance | Notes |
|---|---|---|
| Fixture / demo | `t3.large` | Default template parameter |
| Full local models | `t3.xlarge`+ | Measure RSS before enabling llama.cpp 7B |

Estimated cost: **$25–35** for a short build window with stop/start between sessions.

## Deploy

```bash
aws cloudformation deploy \
  --template-file infra/aws/template.yaml \
  --stack-name peter-pan-demo \
  --parameter-overrides InstanceType=t3.large AllowedIngressCidr=<your-ip>/32 EnableBedrock=false \
  --capabilities CAPABILITY_NAMED_IAM
```

## Validate locally

```powershell
pip install cfn-lint
cfn-lint infra/aws/template.yaml
```

## Teardown

```bash
aws cloudformation delete-stack --stack-name peter-pan-demo
```

## Security notes

- IAM role: SSM by default; optional `EnableBedrock=true` adds Anthropic-only invoke access for Stage C
- EBS encrypted
- HTTPS ingress requires an explicit restricted CIDR; `0.0.0.0/0` is rejected
- Egress is limited to HTTPS and VPC DNS
- Secrets via SSM Parameter Store / `.env` on instance — never committed
- The public subnet/default route is a declared single-instance demo trade-off, not a production topology
