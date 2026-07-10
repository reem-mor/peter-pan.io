---
doc_id: "orders_api_deploy_incident"
title: "Orders API Deployment Incident — INC-20260610-001"
doc_type: "incident"
services: "orders-api, payments-api"
environments: "production"
severity_applicable: "P1"
tags: "historical, orders-api, deployment, rollback, incident"
last_updated: "2026-06-10"
author: "Platform Engineering"
version: "1.0"
---

# Orders API Deployment Incident — INC-20260610-001

## Summary

P1 in production: orders-api order-creation error rate reached 85% within 8 minutes of a deployment that introduced a serialization bug in the checkout-to-payments-api call.

## Timeline

- 2026-06-10 14:02 UTC: orders-api deployment v482 rolled out.
- 2026-06-10 14:07 UTC: order-creation error rate alert fires (85% failure).
- 2026-06-10 14:11 UTC: on-call correlates the spike with deployment v482 and begins rollback per the deployment rollback runbook.
- 2026-06-10 14:19 UTC: rollback to v481 complete; error rate returns below 1%.

## Root Cause

The v482 release changed the payment-authorization request payload without updating payments-api's schema validation, causing every checkout request to be rejected.

## Resolution

Rolled back orders-api to the previous version (v481); confirmed order-creation success rate recovered; opened a follow-up ticket to add a contract test between orders-api and payments-api before re-releasing.

## Reuse Guidance

When a new incident shows orders-api errors starting within an hour of a deployment, follow the orders_api_error_spike runbook first and prepare rollback per the deployment_rollback runbook while continuing dependency checks.
