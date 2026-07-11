---
doc_id: "shop_web"
title: "Shop Web Service Context"
doc_type: "service"
services: "shop-web"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "service ownership, storefront, frontend, ui"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Shop Web Service Context

Shop-web is the customer-facing storefront UI: product browsing, cart, and checkout handoff to orders-api and payments-api.

## Owner

- Team: App Platform
- Primary escalation: Primary App Platform On-Call
- Secondary escalation: Secondary App Platform On-Call
- Channel: `#app-platform`

## Dependencies

- orders-api for cart and order creation.
- payments-api for checkout payment authorization.
- k8s-ingress for public routing and TLS termination.

## Business Impact

Shop-web is tier-1. A degraded storefront blocks browsing and checkout even when orders-api and payments-api are healthy, so always confirm whether the fault is in shop-web or a downstream dependency before escalating.
