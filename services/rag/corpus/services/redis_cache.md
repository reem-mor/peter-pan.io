---
doc_id: "redis_cache"
title: "Redis Cache Service Context"
doc_type: "service"
services: "redis-cache"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "service ownership, cache, redis, infra"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Redis Cache Service Context

Redis-cache is the shared caching layer for orders-api (cart/session cache) and shop-web (catalog cache), fronting postgres-primary reads.

## Owner

- Team: Infra SRE
- Primary escalation: Primary Infra SRE On-Call
- Secondary escalation: Secondary Infra SRE On-Call
- Channel: `#infra-sre`

## Dependencies

- Consumed by orders-api and shop-web.
- Falls back to postgres-primary reads on a cache miss.

## Business Impact

Redis-cache is tier-1. Degradation increases latency and load on postgres-primary rather than causing an outright outage, but sustained misses can cascade into postgres-primary saturation.
