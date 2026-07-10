---
doc_id: "redis_cache_degradation"
title: "Redis Cache Degradation Runbook"
doc_type: "runbook"
services: "redis-cache, orders-api, shop-web"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "redis, cache, eviction, latency, memory"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Redis Cache Degradation Runbook

Use this runbook when cache hit rate drops, evictions increase, redis-cache latency rises, or orders-api/shop-web slow down due to cache misses hitting postgres-primary directly.

## Investigation Steps (read-only)

1. Check Redis `PING`, primary role, replica health, memory usage, and eviction count (`redis-cli INFO` — read-only).
2. Compare redis-cache latency with orders-api and shop-web request latency.
3. Check whether a recent orders-api or shop-web deployment changed cache-key volume or TTL.
4. Inspect network errors between orders-api pods and redis-cache.
5. Confirm whether failover is active, partial, or stuck.

## Triage Decision Tree

- If Redis memory is above 90% and evictions are increasing, reduce cache-write pressure and scale memory.
- If the primary is unavailable, follow the managed Redis failover process.
- If only orders-api sees errors, inspect client pool size and connection reuse.

## Remediation

1. Disable a noisy cache-write path or reduce TTL churn if introduced by a recent deployment.
2. Scale redis-cache memory or shard capacity if safe and pre-approved.
3. Restart orders-api/shop-web clients only after confirming redis-cache itself is healthy.
4. Avoid `FLUSHDB` in production unless the incident commander and Infra SRE owner approve.

## Verification

- Redis latency returns to normal.
- Evictions stop increasing.
- orders-api and shop-web latency and cache hit rate recover.

## Escalation

Escalate to Infra SRE for redis-cache capacity or failover, and to App Platform if orders-api client-side pooling is implicated.
