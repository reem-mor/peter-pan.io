# Proposed deletions / cleanup (Layer 2 validation)

Do **not** delete these without a second confirmation:

| Path | Reason | Recommendation |
|------|--------|----------------|
| `scripts/_ec2_layer2_probe.sh` | One-shot SSH probe | Delete after validation |
| `scripts/_ec2_layer2_scenarios.sh` | One-shot scenario runner | Delete after validation |
| `scripts/_ec2_layer2_followup.sh` | One-shot follow-up | Delete after validation |
| `scripts/_ec2_layer2_guard_dash.sh` | One-shot guard/dash | Delete after validation |
| `scripts/_ec2_dash_overwrite.sh` | One-shot dashboard | Delete after validation |
| Cloud inactive duplicate workflows | Already archived on EC2 | Keep archived; do not recreate |
| Image Analyzer service | Optional vision fallback | **Keep** — course crosswalk |
| PyTorch / torch_classifier | Required for Predictor | **Keep** |
| LangGraph agent | Required for complex path | **Keep** |
| RAGAS / Langfuse | Not present | **Do not add** |

Operator action remaining (manual, not a deletion):

1. In n8n Cloud UI, edit **Header Auth account** so the HTTP header **name** is
   `X-Peter-Webhook-Secret` (not the account display name).
2. Prefer demo via **EC2 on-instance n8n**, not Cloud webhook, until (1) is done.
