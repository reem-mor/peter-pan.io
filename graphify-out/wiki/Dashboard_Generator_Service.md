# Dashboard Generator Service

> 56 nodes · cohesion 0.06

## Key Concepts

- **validator.py** (11 connections) — `services/dashboard-generator/dashboard_generator/validator.py`
- **app.py** (10 connections) — `services/dashboard-generator/dashboard_generator/app.py`
- **grafana_client.py** (9 connections) — `services/dashboard-generator/dashboard_generator/grafana_client.py`
- **validate_dashboard_payload()** (9 connections) — `services/dashboard-generator/dashboard_generator/validator.py`
- **GrafanaClient** (8 connections) — `services/dashboard-generator/dashboard_generator/grafana_client.py`
- **create_dashboard()** (7 connections) — `services/dashboard-generator/dashboard_generator/app.py`
- **fixtures_loader.py** (7 connections) — `services/dashboard-generator/dashboard_generator/fixtures_loader.py`
- **FixtureGrafanaClient** (7 connections) — `services/dashboard-generator/dashboard_generator/grafana_client.py`
- **get_grafana_client()** (7 connections) — `services/dashboard-generator/dashboard_generator/grafana_client.py`
- **assert_valid_dashboard()** (7 connections) — `services/dashboard-generator/dashboard_generator/validator.py`
- **DashboardValidationError** (7 connections) — `services/dashboard-generator/dashboard_generator/validator.py`
- **.post_dashboard()** (5 connections) — `services/dashboard-generator/dashboard_generator/grafana_client.py`
- **Any** (5 connections)
- **DashboardRequest** (4 connections) — `services/dashboard-generator/dashboard_generator/app.py`
- **DashboardResponse** (4 connections) — `services/dashboard-generator/dashboard_generator/app.py`
- **.post_dashboard()** (4 connections) — `services/dashboard-generator/dashboard_generator/grafana_client.py`
- **.substitute_datasource()** (4 connections) — `services/dashboard-generator/dashboard_generator/grafana_client.py`
- **GrafanaPoster** (4 connections) — `services/dashboard-generator/dashboard_generator/grafana_client.py`
- **auth.py** (3 connections) — `services/dashboard-generator/dashboard_generator/auth.py`
- **allowed_metric_names()** (3 connections) — `services/dashboard-generator/dashboard_generator/fixtures_loader.py`
- **load_fixture()** (3 connections) — `services/dashboard-generator/dashboard_generator/fixtures_loader.py`
- **metrics_catalog()** (3 connections) — `services/dashboard-generator/dashboard_generator/fixtures_loader.py`
- **_resolve_fixtures_dir()** (3 connections) — `services/dashboard-generator/dashboard_generator/fixtures_loader.py`
- **_panel_rect()** (3 connections) — `services/dashboard-generator/dashboard_generator/validator.py`
- **Any** (3 connections)
- *... and 31 more nodes in this community*

## Relationships

- [Escalation Service](Escalation_Service.md) (1 shared connections)

## Source Files

- `services/dashboard-generator/dashboard_generator/app.py`
- `services/dashboard-generator/dashboard_generator/auth.py`
- `services/dashboard-generator/dashboard_generator/fixtures_loader.py`
- `services/dashboard-generator/dashboard_generator/grafana_client.py`
- `services/dashboard-generator/dashboard_generator/validator.py`

## Audit Trail

- EXTRACTED: 163 (90%)
- INFERRED: 18 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*