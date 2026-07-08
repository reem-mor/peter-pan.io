# Sample Questions and Answers — Live Bedrock KB

- **Run at:** 2026-07-05 19:44:34 UTC
- **Model:** `arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0`
- **Corpus:** s3://<bucket-name>/projects/piter-aiops/knowledge_base/
- **Cases:** 4 grounded runbook answers + 1 off-topic refusal

## 1. What should I check when users cannot log in after the latest deployment?

- **Grounded:** `True` · **Citations:** 4
- **Sources:** `auth_service_login_failure.md`, `auth_service_login_failure.md`, `deployment_rollback.md`, `historical_auth_incidents.md`

**Answer:**

Priority:

Classify P1-P4 based on the impact of the incident. If the login failures started immediately after the latest deployment and affected a significant number of users, classify it as P1 due to the high customer impact and potential service disruption.

Investigation findings:

Check the following based on the "Auth Service Login Failure Runbook" :

1. Confirm the production error rate, affected markets, and whether login failures started within 60 minutes of a deployment.

2. Check recent auth-service deployments, feature flags, schema migrations, and token-signing key changes.

3. Validate auth-service pod health, readiness probes, and `/health/ready` responses.

4. Check Redis token store latency, evictio…

---

## 2. Analyze this alert: high error rate on auth-service in production after deployment.

- **Grounded:** `True` · **Citations:** 2
- **Sources:** `auth_service_login_failure.md`, `historical_auth_incidents.md`

**Answer:**

Priority:

P1 - The high error rate on the auth-service in production after a deployment indicates a significant customer impact, as it affects the ability to log in and access services.

Investigation findings:

The alert suggests a correlation between the recent deployment and the increase in error rates. The investigation should focus on confirming the production error rate, affected markets, and whether login failures started within 60 minutes of the deployment. It is also important to check recent deployments, feature flags, schema migrations, and token-signing key changes.

Triage plan:

1. Confirm the production error rate, affected markets, and whether login failures started within 60 minutes of the deploy…

---

## 3. Who should I escalate this incident to?

- **Grounded:** `True` · **Citations:** 2
- **Sources:** `piter_workflow.md`, `escalation_policies_guide.md`

**Answer:**

To determine who to escalate this incident to, we need to classify the incident's priority first. Based on the severity policy from the search results, here's how you should proceed:

1. **Classify the incident priority** using customer impact, error rate, business criticality, revenue exposure, and regulated-market risk.

2. **Check the severity policy** for guidance on who to notify based on the priority level.

For example:

- **P1**: Notify primary on-call, secondary on-call, incident commander, and service lead immediately.

- **P2**: Notify primary on-call and service lead within 15 minutes.

- **P3**: Notify primary on-call during business hours unless customer impact increases.

- **P4**: Ticket only unless…

---

## 4. Are there similar incidents from the past?

- **Grounded:** `True` · **Citations:** 3
- **Sources:** `similar_incidents_examples.md`, `historical_auth_incidents.md`, `historical_deployment_incidents.md`

**Answer:**

Yes, there are similar incidents from the past. Here are some examples:

1. **Login Failure Similarity Signals** :

- Same service: auth-service.

- Same timing: failure starts after production deployment.

- Same symptoms: login error rate, token validation failure, session loss, 401 for valid users.

- Same dependencies: Redis token store, customer-db, API Gateway.

2. **Historical Auth Incidents** :

- **INC-AUTH-2026-03-08**: Auth-service latency and login timeouts increased after a client-pool change. Root cause was connection pool exhaustion between auth-service and Redis token store.

- **INC-AUTH-2025-10-28**: Login failures affected EU traffic after CDN and gateway configuration drift. Root…

---

## 5. What is the business impact of auth-service login failures in GIB-UKGC production?

- **Grounded:** `True` · **Citations:** 3
- **Sources:** `auth_service_login_failure.md`, `business_impact_guide.md`, `auth_service_login_failure.md`

**Answer:**

Priority:

P1 - Auth-service login failures in the GIB-UKGC production environment are classified as P1 due to the high customer impact, dependency on the service, and potential risk to SLAs.

Investigation findings:

Auth-service login failures in the GIB-UKGC production environment can be traced through the auth-service login failure runbook, which includes checking recent deployments, auth-service pod health, Redis token store status, and customer-db connectivity. Historical incidents and similar incidents examples also provide context for these failures.

Triage plan:

1. Confirm the production error rate and affected markets, and whether login failures started within 60 minutes of a deployment.

2. Check recen…

---
