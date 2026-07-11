---
doc_id: "postgres_primary"
title: "Postgres Primary Service Context"
doc_type: "service"
services: "postgres-primary"
environments: "production, staging"
severity_applicable: "P1,P2,P3"
tags: "service ownership, database, postgres, tier-0"
last_updated: "2026-06-20"
author: "Platform Engineering"
version: "1.0"
---

# Postgres Primary Service Context

Postgres-primary is the primary relational database backing orders-api and payments-api: order records, payment records, and transactional state.

## Owner

- Team: Database Reliability
- Primary escalation: Primary Database Reliability On-Call
- Secondary escalation: Secondary Database Reliability On-Call
- Channel: `#database-reliability`

## Dependencies

- Consumed by orders-api and payments-api.
- No upstream service dependencies.

## Business Impact

Postgres-primary is tier-0. Saturation or connectivity loss stalls every write path in orders-api and payments-api.
