FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rag_service ./rag_service
COPY corpus ./corpus

RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "rag_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
