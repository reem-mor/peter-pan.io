"""RAG microservice — offline TF-IDF retrieval over the PETER PAN corpus.

Self-contained deployment unit (AGENTS.md §2): this package is the service's
own import root. No ``services.*`` cross-imports — other services talk to
this one over HTTP only.
"""

from __future__ import annotations
