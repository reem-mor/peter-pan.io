---
doc_id: "orders_api_error_spike"
title: "Orders API Error Spike Runbook"
doc_type: "runbook"
services: "orders-api, postgres-primary, redis-cache, payments-api"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "orders-api, error rate, deployment, checkout, database, cache"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Orders API Error Spike Runbook

Use this runbook when orders-api error rate rises, checkout or order-creation requests fail, or the error rate increases shortly after a deployment.

## Investigation Steps (read-only)

1. Confirm the current orders-api error rate, affected environment (production or staging), and whether it started within 60 minutes of a deployment (dashboard query).
2. Check recent orders-api deployments and feature flags (`kubectl rollout history`, deployment tool history — read-only).
3. Check postgres-primary connection pool saturation and query latency for orders-api's connections (read-only monitoring query).
4. Check redis-cache latency and hit rate for orders-api's cache calls (`redis-cli INFO` — read-only).
5. Check payments-api health and latency, since checkout failures can originate downstream.

## Triage Decision Tree

- If the latest deployment is within the last hour and errors started immediately after it, prepare rollback first — see the deployment rollback runbook.
- If postgres-primary connections are exhausted or queries are slow, follow the database connectivity runbook.
- If redis-cache hit rate has dropped or evictions are rising, follow the redis cache degradation runbook.
- If payments-api itself is failing, escalate to App Platform's payments-api owner rather than treating this as an orders-api-only incident.

## Remediation

1. Freeze further orders-api releases until the incident commander approves.
2. Roll back the latest orders-api deployment if deployment correlation is strong and a rollback is available.
3. Disable a newly released feature flag on the checkout or order-creation path if it is implicated.
4. Restart only unhealthy orders-api pods after capturing logs.
5. Validate order-creation success rate before declaring mitigation.

## Verification

- `orders_api_error_rate` returns below 1% for 10 minutes.
- `orders_api_success_rate` (checkout completion) returns to baseline.
- No new postgres-primary or redis-cache alerts fire.

## Escalation

Escalate P1/P2 orders-api incidents to App Platform primary on-call, then secondary on-call if no acknowledgement within the policy window. Produce a safe escalation preview only; do not send real escalation messages automatically.
