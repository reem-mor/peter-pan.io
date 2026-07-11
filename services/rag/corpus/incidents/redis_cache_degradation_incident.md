---
doc_id: "redis_cache_degradation_incident"
title: "Redis Cache Degradation — INC-20260625-003"
doc_type: "incident"
services: "redis-cache, orders-api"
environments: "production"
severity_applicable: "P3"
tags: "historical, redis-cache, eviction, latency, incident"
last_updated: "2026-06-25"
author: "Platform Engineering"
version: "1.0"
---

# Redis Cache Degradation — INC-20260625-003

## Summary

P3 in production: redis-cache memory pressure caused an eviction storm, dropping cache hit rate and increasing orders-api latency as reads fell through to postgres-primary.

## Timeline

- 2026-06-25 17:10 UTC: redis-cache memory usage crosses 90%; eviction count begins climbing.
- 2026-06-25 17:16 UTC: orders-api p95 latency doubles as cache hit rate drops below 60%.
- 2026-06-25 17:22 UTC: on-call confirms redis-cache primary is healthy but memory-constrained, following the redis cache degradation runbook.
- 2026-06-25 17:35 UTC: redis-cache memory scaled up; evictions stop; orders-api latency and cache hit rate recover by 17:45 UTC.

## Root Cause

A gradual increase in cached cart-session keys without a matching memory scale-up led to sustained eviction pressure.

## Resolution

Scaled redis-cache memory capacity, restarted orders-api clients after confirming redis-cache health, and monitored hit-rate recovery. Added a follow-up to alert on memory usage before evictions start.

## Reuse Guidance

When cache hit rate drops and a downstream service's latency rises in step, follow the redis_cache_degradation runbook and check memory/eviction trend before assuming a client-side connection issue.
