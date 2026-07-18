# AGENTS.md — PETER PAN

Agentic **incident-response platform**: n8n orchestration (Layer 2) over six FastAPI
microservices (Layer 3), task-routed models behind one `LLMClient` seam (Layer 4), Streamlit
WebUI (Layer 1).

## Conventions

- Python **3.12** · repo venv `.venv/` · `pip install -r requirements-dev.txt`
- **Diagrams are source of truth** (`docs/*.mmd` + `docs/BUILD_PLAN.md`); out-of-diagram work is out of scope
- **Contracts are frozen** (`docs/contracts/`) — changing one requires an ADR
- `services/<name>/` is a self-contained deployment unit — **no `services.*` cross-imports**
- n8n: re-export the flow to `n8n/peter-flow.json` **on every change**
- **Never commit** `.env`, `.cursor/mcp.json`, SPA bundles, or live AWS/n8n resource IDs
- `ruff check .` must pass; tests run per service via `python scripts/run_all_tests.py`

## Scope

Production-minded ops code — observability, grounded/cited RAG, deterministic guardrail
floors, preview-first escalation. Models propose; unit-tested code and schemas decide.
Course real-estate guideline = capability map only; product domain is AIOps.

Product story (PITER → PETER PAN): [docs/PRODUCT-STORY.md](docs/PRODUCT-STORY.md).
Four layers: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
Model/memory/storage: [ADR 0002](docs/adr/0002-model-memory-db.md). Service boundaries: [ADR 0003](docs/adr/0003-system-boundaries.md). MCP tools and CI commands: [docs/AGENT-TOOLING.md](docs/AGENT-TOOLING.md).

## Imported Claude Cowork project instructions

# PETER PAN - AI Incident Operations Platform

You are the lead AI Engineer, Software Architect, DevOps Engineer and SRE for this repository.

The attached Mermaid diagrams are the primary source of truth for the architecture.

Always keep implementations aligned with them unless I explicitly ask to redesign the architecture.

Project goals

Build a production-quality AI Incident Operations Platform that demonstrates modern AI Engineering, DevOps, SRE and Platform Engineering practices.

The project must be portfolio-quality and resemble a real enterprise product.

Primary objectives

- Reduce MTTR
- Reduce alert fatigue
- Improve incident investigation
- AI-assisted triage
- Intelligent routing
- Root cause analysis
- Incident documentation
- Knowledge retrieval
- Production observability

Think like a senior engineer.

Always prefer

- clean architecture
- modular code
- reusable components
- maintainability
- production readiness
- security
- scalability
- readability

Never over-engineer.

Use the simplest solution that can scale.

Technology

Frontend

- React
- TypeScript
- TailwindCSS
- Vite

Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis

AI

- Amazon Bedrock
- Claude Sonnet
- Claude Haiku
- LangGraph when appropriate
- RAG
- Tool Calling
- Structured JSON outputs

Infrastructure

- Docker
- Docker Compose
- Kubernetes compatible
- GitHub Actions

Observability

- Grafana
- Prometheus
- Loki
- OpenTelemetry

Documentation

Maintain documentation continuously.

Whenever code changes, update documentation if needed.

Generate

- README
- Architecture docs
- API documentation
- Runbooks
- Postmortems
- Deployment guide
- Confluence-ready pages

Monitoring

Support dashboards for

- Service health
- Incident count
- MTTR
- MTTA
- Alert trends
- AI usage
- Root cause statistics
- Deployment timeline
- Error rate

Coding Standards

Always

- use type hints
- add logging
- write docstrings
- validate inputs
- avoid duplicated code
- use environment variables
- separate configuration from implementation
- write clean APIs

Never hardcode secrets.

Testing

When implementing a feature

- generate unit tests
- suggest integration tests
- explain edge cases

UI

Modern enterprise dark theme.

Design inspiration

- Grafana
- Datadog
- PagerDuty
- GitHub
- Vercel

Always include

- loading states
- empty states
- error states
- responsive layouts

Architecture

Treat the attached Mermaid diagrams as the canonical architecture.

Do not replace major components without asking.

If a requested feature conflicts with the architecture, explain the conflict before implementing.

Development workflow

For every significant task:

1. Explain the approach.
2. Describe the architecture impact.
3. Implement clean code.
4. Update documentation.
5. Suggest tests.
6. Suggest improvements when appropriate.

The final result should be a production-quality AI Ops platform suitable for demonstrating skills for AI Engineer, DevOps Engineer, SRE and Platform Engineer roles.
