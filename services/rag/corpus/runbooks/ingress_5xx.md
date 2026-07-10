---
doc_id: "ingress_5xx"
title: "K8s Ingress 5xx Troubleshooting Runbook"
doc_type: "runbook"
services: "k8s-ingress, shop-web, orders-api, payments-api"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "ingress, 5xx, edge, routing, timeout, kubernetes"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# K8s Ingress 5xx Troubleshooting Runbook

Use this runbook when k8s-ingress returns 5xx, 502, 503, or 504 errors for production or staging traffic.

## Investigation Steps (read-only)

1. Check ingress controller logs and error rate by route/host (read-only: `kubectl logs`, dashboard query).
2. Compare ingress 5xx with backend pod health and readiness probes for shop-web, orders-api, and payments-api (`kubectl get pods`, `kubectl describe ingress`).
3. Check recent ingress or routing configuration changes (`kubectl rollout history` on the ingress controller deployment).
4. Inspect upstream timeout settings, TLS certificate expiry, and backend connection limits.
5. Confirm whether synthetic checks fail from multiple regions or only one.

## Triage Decision Tree

- If backend errors mirror ingress errors, follow the backend service's own runbook.
- If backends are healthy but ingress fails, inspect ingress route/config and TLS certificate state.
- If only one backend's routes fail, scope the incident to that service and its owner.

## Remediation

1. Roll back the most recent ingress configuration change if it correlates with the failure.
2. Shift traffic away from an unhealthy backend only if multiple healthy replicas remain.
3. Renew or reattach an expiring TLS certificate through the approved certificate pipeline.
4. Avoid deleting or recreating the ingress resource during an active incident.

## Verification

- Ingress 5xx rate drops below 1%.
- p99 latency returns to baseline.
- Synthetic checks pass for shop-web, orders-api, and payments-api routes.

## Escalation

Escalate to Infra SRE for ingress/TLS/routing issues, and to the backend service owner (App Platform) when backend errors mirror ingress errors.
