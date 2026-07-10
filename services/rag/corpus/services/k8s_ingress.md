---
doc_id: "k8s_ingress"
title: "K8s Ingress Service Context"
doc_type: "service"
services: "k8s-ingress"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "service ownership, ingress, edge, routing, tier-0"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# K8s Ingress Service Context

K8s-ingress owns public routing, TLS termination, and path-based routing to shop-web, orders-api, and payments-api.

## Owner

- Team: Infra SRE
- Primary escalation: Primary Infra SRE On-Call
- Secondary escalation: Secondary Infra SRE On-Call
- Channel: `#infra-sre`

## Dependencies

- Routes to shop-web, orders-api, and payments-api.
- TLS certificate management.

## Business Impact

K8s-ingress is tier-0. Ingress incidents can make every healthy backend service unreachable; always compare ingress 5xx with backend 5xx before escalating to a backend owner.
