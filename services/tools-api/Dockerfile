# Tools API — self-contained deployment unit (BUILD_PLAN.md §2).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tools_api/ tools_api/
COPY data/ data/
COPY schemas/ schemas/

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

ENV TOOLS_DATA_DIR=/app/data \
    TOOLS_AUDIT_DB=/app/audit.sqlite

EXPOSE 8000

CMD ["uvicorn", "tools_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
