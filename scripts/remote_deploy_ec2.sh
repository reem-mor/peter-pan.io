#!/usr/bin/env bash
# Remote-side deploy steps — invoked via SSH from scripts/deploy_ec2.ps1
set -euo pipefail
mkdir -p ~/peter-pan
tar -xzf /tmp/peter-pan.tgz -C ~/peter-pan
rm -f /tmp/peter-pan.tgz
cd ~/peter-pan
if [ ! -f .env ]; then
  gen() { openssl rand -hex 24; }
  umask 177
  {
    echo "PETER_SERVICES_TOKEN=$(gen)"
    echo "PETER_WEBHOOK_SECRET=$(gen)"
    echo "PETER_RUNTIME_MODE=demo"
    echo "N8N_ENCRYPTION_KEY=$(gen)"
    echo "N8N_JWT_SECRET=$(gen)"
    echo "N8N_OWNER_EMAIL=admin@local.peter"
    echo "N8N_OWNER_PASSWORD=Pp7-$(gen)"
  } > .env
  umask 022
  echo "generated fresh instance .env"
fi
docker compose -f docker-compose.yml -f docker-compose.ec2.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.ec2.yml --profile bootstrap run --rm -T n8n-bootstrap < /dev/null
echo "--- on-instance health check ---"
fails=0
for port in 8001 8002 8003 8004 8005 8006 8007 8008 8020 3000 5678; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${port}/healthz" 2>/dev/null || echo 000)
  echo "port ${port}: ${code}"
  [ "$code" = "200" ] || fails=$((fails+1))
done
code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:8010/healthz" 2>/dev/null || echo 000)
echo "port 8010 (loopback seam): ${code}"
[ "$fails" -eq 0 ] || { echo "health check failed (${fails})"; exit 1; }
echo "all public services healthy on-instance"
