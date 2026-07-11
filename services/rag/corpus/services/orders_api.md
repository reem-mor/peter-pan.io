---
doc_id: "orders_api"
title: "Orders API Service Context"
doc_type: "service"
services: "orders-api"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "service ownership, orders, checkout, tier-0"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Orders API Service Context

Orders-api owns order creation, cart-to-order conversion, order status, and checkout orchestration between shop-web and payments-api.

## Owner

- Team: App Platform
- Primary escalation: Primary App Platform On-Call
- Secondary escalation: Secondary App Platform On-Call
- Channel: `#app-platform`

## Dependencies

- postgres-primary for order storage.
- redis-cache for cart/session cache.
- payments-api for payment authorization.

## Business Impact

Orders-api is tier-0. Order-creation failures block all checkout revenue immediately.
