---
doc_id: "database_connectivity"
title: "Database Connectivity Runbook"
doc_type: "runbook"
services: "postgres-primary, orders-api, payments-api"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "database, postgres, connectivity, cpu, pool, locks"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Database Connectivity Runbook

Use this runbook for postgres-primary CPU saturation, connection pool exhaustion, lock waits, replica lag, or orders-api/payments-api database errors.

## Investigation Steps (read-only)

1. Check postgres-primary CPU, active connections, connection pool saturation, lock waits, and slow queries (read-only monitoring query, `pg_stat_activity`).
2. Compare database symptoms with the orders-api and payments-api deployment timeline.
3. Identify whether failures are reads, writes, or specific to one service's connection pool.
4. Check replica lag before shifting read traffic.
5. Inspect the top queries and recent migrations for missing indexes or long-running transactions (read-only `EXPLAIN`).

## Triage Decision Tree

- If CPU is high with one dominant query, mitigate the query or roll back the service that introduced it.
- If connections are exhausted, reduce client pool pressure (orders-api/payments-api pool size) before killing database sessions.
- If a migration lock is blocking orders-api or payments-api, involve the DBA and service owner immediately.
- If replica lag affects reads only, remove the lagging replica from rotation.

## Remediation

1. Stop the newest deployment or feature flag that created the load.
2. Reduce orders-api/payments-api replica count or connection pool size if the database is overloaded by clients.
3. Kill only confirmed blocking sessions with DBA approval.
4. Roll back a schema or application change only when the rollback plan is verified.

## Verification

- CPU remains below alert threshold for 10 minutes.
- Connection pool saturation clears.
- orders-api and payments-api write success rates return to baseline.
- No new lock waits accumulate.

## Escalation

Escalate to Database Reliability for P1/P2 database incidents. Include service, query evidence, deployment correlation, business impact, and rollback status.
