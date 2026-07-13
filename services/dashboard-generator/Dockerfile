FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard_generator ./dashboard_generator
COPY fixtures/dashboards ./dashboard_generator/fixtures

RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "dashboard_generator.app:app", "--host", "0.0.0.0", "--port", "8000"]
