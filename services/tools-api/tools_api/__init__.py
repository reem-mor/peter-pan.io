"""Tools API — owners, deploys, similar incidents, and preview-only escalation.

Self-contained FastAPI microservice (BUILD_PLAN.md §2): this package is its own
import root. No ``services.*`` cross-imports — every dependency on another
PETER PAN service is HTTP-only.
"""

from __future__ import annotations
