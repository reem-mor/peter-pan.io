---
doc_id: "payments_api"
title: "Payments API Service Context"
doc_type: "service"
services: "payments-api"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "service ownership, payments, checkout, tier-0"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Payments API Service Context

Payments-api owns payment authorization, provider routing, and payment status callbacks for orders-api checkout.

## Owner

- Team: App Platform
- Primary escalation: Primary App Platform On-Call
- Secondary escalation: Secondary App Platform On-Call
- Channel: `#app-platform`

## Dependencies

- postgres-primary for payment records.
- orders-api for checkout orchestration.
- External payment provider (outside this corpus).

## Business Impact

Payments-api is tier-0. Payment-authorization failures block checkout completion and cause direct revenue loss.
