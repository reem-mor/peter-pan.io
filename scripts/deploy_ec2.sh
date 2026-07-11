#!/usr/bin/env bash
# Deploy the PETER PAN stack to the provisioned EC2 instance (idempotent).
#
# - Packages the working tree via `git ls-files -co --exclude-standard`,
#   so gitignored files (.env, PEM keys, .cursor/mcp.json) can never leak.
# - Generates a FRESH .env on the instance on first deploy (local secrets are
#   never transferred); subsequent deploys keep it so n8n keys stay stable.
# - Brings up docker-compose.yml + docker-compose.ec2.yml, runs the n8n
#   bootstrap profile, then health-checks all services on-instance.
#
# Usage: bash scripts/deploy_ec2.sh [public-ip]
set -euo pipefail

REGION="${AWS_REGION:-$(aws configure get region)}"
NAME_TAG="peter-pan-stage-a"
KEY_FILE="${HOME}/.ssh/peter-pan-key.pem"
REMOTE_DIR="peter-pan"

log() { printf '>>> %s\n' "$*"; }

IP="${1:-}"
if [[ -z "$IP" ]]; then
  IP="$(aws ec2 describe-instances --region "$REGION" \
    --filters Name=tag:Name,Values="$NAME_TAG" Name=instance-state-name,Values=running \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)"
fi
[[ "$IP" != "None" && -n "$IP" ]] || { echo "no running ${NAME_TAG} instance found" >&2; exit 1; }
[[ -f "$KEY_FILE" ]] || { echo "missing ${KEY_FILE} — run scripts/provision_ec2.sh first" >&2; exit 1; }
log "Deploying to ubuntu@${IP}"

SSH_OPTS=(-i "$KEY_FILE" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10)

log "Waiting for SSH ..."
for _ in $(seq 1 30); do
  ssh "${SSH_OPTS[@]}" ubuntu@"$IP" true 2>/dev/null && break
  sleep 10
done
ssh "${SSH_OPTS[@]}" ubuntu@"$IP" true

log "Waiting for cloud-init (Docker install) to finish ..."
ssh "${SSH_OPTS[@]}" ubuntu@"$IP" 'cloud-init status --wait >/dev/null 2>&1 || true; docker --version && docker compose version'

log "Packaging working tree (tracked + untracked, .gitignore respected) ..."
REPO_ROOT="$(git rev-parse --show-toplevel)"
TARBALL="$(mktemp).tgz"
git -C "$REPO_ROOT" ls-files -co --exclude-standard -z \
  | tar -C "$REPO_ROOT" --null -T - -czf "$TARBALL"
scp "${SSH_OPTS[@]}" "$TARBALL" ubuntu@"$IP":/tmp/peter-pan.tgz
rm -f "$TARBALL"

log "Extracting, generating instance .env (first deploy only), starting stack ..."
ssh "${SSH_OPTS[@]}" ubuntu@"$IP" REMOTE_DIR="$REMOTE_DIR" 'bash -s' <<'REMOTE'
set -euo pipefail
mkdir -p "$HOME/$REMOTE_DIR"
tar -xzf /tmp/peter-pan.tgz -C "$HOME/$REMOTE_DIR"
rm -f /tmp/peter-pan.tgz
cd "$HOME/$REMOTE_DIR"

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
  echo "generated fresh instance .env (600, values never leave the instance)"
fi

docker compose -f docker-compose.yml -f docker-compose.ec2.yml up -d --build
# -T + </dev/null: `compose run` attaches stdin by default and would swallow
# the remainder of this bash -s heredoc, silently skipping the health check.
docker compose -f docker-compose.yml -f docker-compose.ec2.yml --profile bootstrap run --rm -T n8n-bootstrap < /dev/null

echo "--- on-instance health check ---"
fails=0
for port in 8001 8002 8003 8004 8005 8006 8007 8010 8020 5678; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${port}/healthz" || echo 000)"
  echo "port ${port}: ${code}"
  [ "$code" = "200" ] || fails=$((fails+1))
done
[ "$fails" -eq 0 ] || { echo "health check failed (${fails})"; exit 1; }
echo "all services healthy on-instance"
REMOTE

log "DEPLOYED — validate externally with:"
log "  python scripts/test_layer3_health.py --base-url http://${IP}"
