FROM python:3.12-slim

WORKDIR /app
RUN useradd --create-home --shell /bin/bash appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fixture_llm/ fixture_llm/
USER appuser
EXPOSE 8000
CMD ["uvicorn", "fixture_llm.app:app", "--host", "0.0.0.0", "--port", "8000"]
