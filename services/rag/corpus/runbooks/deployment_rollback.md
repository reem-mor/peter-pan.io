---
doc_id: "deployment_rollback"
title: "Deployment Rollback Runbook"
doc_type: "runbook"
services: "orders-api, payments-api, shop-web, k8s-ingress"
environments: "production, staging"
severity_applicable: "P1,P2"
tags: "deployment, rollback, release, mitigation"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Deployment Rollback Runbook

Use this runbook when an incident begins soon after a release and the service has a known rollback path.

## Investigation Steps (read-only)

1. Identify the latest production or staging deployment for the affected service and its dependencies (deployment history query — read-only).
2. Compare deployment time with alert start time and customer-impact timeline.
3. Confirm rollback availability, prior version, and database migration compatibility.
4. Check whether a feature flag or configuration revert is safer than a code rollback.
5. Announce rollback intent in the incident channel with service, version, and expected impact.

## Triage Decision Tree

- Roll back when a release occurred within 60 minutes, metrics degraded after release, and rollback is available.
- Prefer feature flag rollback when only a new code path is affected.
- Do not roll back database migrations blindly; involve the owning team and Database Reliability if schema changes are present.

## Remediation

1. Freeze further deployments for the affected service.
2. Execute the approved rollback command or CI/CD rollback job.
3. Watch rollout status until all pods are healthy.
4. Validate customer-facing success metrics for at least 10 minutes.
5. Open a follow-up ticket for the failed release before unfreezing deployments.

## Verification

- Error rate, latency, and saturation return to baseline.
- No new alerts fire for the same service.
- The previous version is confirmed in the deployment inventory.

## Escalation

For P1 rollback, notify the service owner, incident commander, and platform release owner. For P2 rollback, notify the service owner and release owner.
