FROM python:3.12-slim-bookworm

COPY scripts/n8n-bootstrap-requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
