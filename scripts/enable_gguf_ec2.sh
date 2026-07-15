#!/usr/bin/env bash
# Session D — GGUF on EBS + llama-cpp-python for the RAG generator path.
# Idempotent: safe to re-run after deploy. Run on EC2 from ~/peter-pan after
# docker-compose.ec2.yml mounts /home/ubuntu/models → /models in rag.
set -euo pipefail

REPO="${REPO:-$HOME/peter-pan}"
MODEL_DIR="${MODEL_DIR:-/home/ubuntu/models}"
MODEL_FILE="mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/${MODEL_FILE}"
CONTAINER_GGUF="/models/${MODEL_FILE}"
ENV_FILE="${REPO}/.env"
COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.ec2.yml)

cd "$REPO"

echo "=== disk / memory headroom ==="
df -h /
free -h

mkdir -p "$MODEL_DIR"

if [ ! -f "$MODEL_PATH" ]; then
  echo "Downloading ${MODEL_FILE} (~4.4GB) to ${MODEL_DIR}..."
  curl -fL --retry 3 --retry-delay 5 -o "${MODEL_PATH}.part" "$MODEL_URL"
  mv "${MODEL_PATH}.part" "$MODEL_PATH"
fi
ls -lh "$MODEL_PATH"

patch_env() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    sed -i "s|^${key}=.*|${key}=${val}|" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

patch_env GGUF_MODEL_PATH "$CONTAINER_GGUF"
grep -q '^PETER_VECTOR_BACKEND=' "$ENV_FILE" || patch_env PETER_VECTOR_BACKEND chroma

echo "=== rebuild rag (llama-cpp-python) ==="
"${COMPOSE[@]}" build rag
"${COMPOSE[@]}" up -d --force-recreate rag

echo "=== wait for rag /healthz ==="
for _ in $(seq 1 45); do
  code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8003/healthz 2>/dev/null || echo 000)
  [ "$code" = "200" ] && break
  sleep 3
done
curl -s http://localhost:8003/healthz
echo

echo "=== llama_cpp import ==="
"${COMPOSE[@]}" exec -T rag python -c "import llama_cpp; print('llama_cpp OK', llama_cpp.__version__)"

echo "=== GGUF mount in container ==="
"${COMPOSE[@]}" exec -T rag ls -lh "$CONTAINER_GGUF"

echo "=== generator smoke (Chroma + GGUF) ==="
timeout 900 "${COMPOSE[@]}" exec -T \
  -e GGUF_MODEL_PATH="$CONTAINER_GGUF" \
  -e PETER_VECTOR_BACKEND=chroma \
  -e CHROMA_PATH=/data/chroma \
  rag python - <<'PY'
import re
import sys

from rag_service.generator import get_generator
from rag_service.vector_rag import get_vector_retriever

query = "orders-api 5xx error rate surge right after a release"
hits = get_vector_retriever().search(query, top_k=3)
print("hits:", [(h.doc_id, round(h.score, 3)) for h in hits])
generator = get_generator()
if generator is None:
    print("FAIL: generator unavailable")
    sys.exit(1)
insight = generator.generate(query, [h.excerpt for h in hits])
print("--- insight ---")
print(insight or "(empty)")
if not insight or not re.search(r"INC-\d+", insight):
    sys.exit(1)
PY

echo "=== live POST /query ==="
TOKEN=$(grep '^PETER_SERVICES_TOKEN=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r')
printf '%s\n' '{"query":"orders-api 5xx error rate surge right after a release"}' >/tmp/q.json
timeout 900 curl -s -X POST http://localhost:8003/query \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${TOKEN}" \
  --data @/tmp/q.json
echo
echo "Session D GGUF enable complete."
