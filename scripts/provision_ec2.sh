#!/usr/bin/env bash
# Provision the PETER PAN Stage A demo EC2 instance (idempotent).
#
# Security floor (non-negotiable):
#   - The Security Group admits ONLY the caller's current public IP (/32).
#     Never 0.0.0.0/0. Any existing wide rule on the SG is revoked.
#   - n8n runs ON the instance inside the compose network, so no external
#     "n8n IP" rule is needed — service-to-service calls never leave the host.
#   - IMDSv2 required; keypair PEM is written to ~/.ssh (never the repo).
#
# Ports (project map, see evaluation/run_e2e.py):
#   22 ssh · 8001-8006 core services · 8020 integration-stubs · 5678 n8n UI
#
# Usage: bash scripts/provision_ec2.sh
set -euo pipefail
export MSYS_NO_PATHCONV=1  # Git Bash: stop mangling /aws/... args into Windows paths

REGION="${AWS_REGION:-$(aws configure get region)}"
: "${REGION:?No AWS region configured (aws configure set region ...)}"
INSTANCE_TYPE="${PETER_EC2_TYPE:-t3.large}"
NAME_TAG="peter-pan-stage-a"
SG_NAME="peter-pan-sg"
KEY_NAME="peter-pan-key"
KEY_FILE="${HOME}/.ssh/${KEY_NAME}.pem"
VOLUME_GB=30
SERVICE_PORTS=(22 3000 8001 8002 8003 8004 8005 8006 8007 8008 8020 5678)

log() { printf '>>> %s\n' "$*"; }

DEV_IP="$(curl -fsS https://checkip.amazonaws.com | tr -d '[:space:]')"
[[ "$DEV_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "could not determine dev public IP" >&2; exit 1; }
log "Region ${REGION}; sole inbound source: ${DEV_IP}/32"

VPC_ID="$(aws ec2 describe-vpcs --region "$REGION" \
  --filters Name=is-default,Values=true \
  --query 'Vpcs[0].VpcId' --output text)"
[[ "$VPC_ID" != "None" ]] || { echo "no default VPC in ${REGION}" >&2; exit 1; }

# --- Security group (create-if-missing, rules pinned to dev IP) -------------
SG_ID="$(aws ec2 describe-security-groups --region "$REGION" \
  --filters Name=group-name,Values="$SG_NAME" Name=vpc-id,Values="$VPC_ID" \
  --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo None)"
if [[ "$SG_ID" == "None" ]]; then
  SG_ID="$(aws ec2 create-security-group --region "$REGION" \
    --group-name "$SG_NAME" --vpc-id "$VPC_ID" \
    --description "PETER PAN Stage A - dev IP only, never 0.0.0.0/0" \
    --query 'GroupId' --output text)"
  log "Created SG ${SG_ID}"
else
  log "Reusing SG ${SG_ID}"
fi

# Revoke any world-open inbound rule that may have crept in.
WIDE_RULES="$(aws ec2 describe-security-groups --region "$REGION" --group-ids "$SG_ID" \
  --query 'SecurityGroups[0].IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]' --output json)"
if [[ "$WIDE_RULES" != "[]" ]]; then
  log "Revoking world-open inbound rules (policy: never 0.0.0.0/0)"
  aws ec2 revoke-security-group-ingress --region "$REGION" --group-id "$SG_ID" \
    --ip-permissions "$WIDE_RULES"
fi

for port in "${SERVICE_PORTS[@]}"; do
  aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" \
    --protocol tcp --port "$port" --cidr "${DEV_IP}/32" >/dev/null 2>&1 \
    || true  # duplicate rule -> already authorized
done
log "SG inbound: ports ${SERVICE_PORTS[*]} from ${DEV_IP}/32 only"

# --- Keypair -----------------------------------------------------------------
if [[ ! -f "$KEY_FILE" ]]; then
  if aws ec2 describe-key-pairs --region "$REGION" --key-names "$KEY_NAME" >/dev/null 2>&1; then
    log "AWS keypair exists but local PEM is missing — recreating keypair"
    aws ec2 delete-key-pair --region "$REGION" --key-name "$KEY_NAME"
  fi
  mkdir -p "$(dirname "$KEY_FILE")"
  # tr strips the CRLF the AWS CLI emits on Windows — OpenSSH rejects CRLF keys.
  aws ec2 create-key-pair --region "$REGION" --key-name "$KEY_NAME" \
    --key-type ed25519 --query 'KeyMaterial' --output text | tr -d '\r' > "$KEY_FILE"
  chmod 600 "$KEY_FILE"
  log "Keypair written to ${KEY_FILE} (never commit this)"
else
  log "Reusing keypair ${KEY_FILE}"
fi

# --- AMI: Ubuntu 24.04 LTS (canonical-owned, via public SSM parameter) -------
AMI_ID="$(aws ssm get-parameter --region "$REGION" \
  --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
  --query 'Parameter.Value' --output text)"
log "Ubuntu 24.04 AMI: ${AMI_ID}"

# --- Instance (reuse if running) ---------------------------------------------
INSTANCE_ID="$(aws ec2 describe-instances --region "$REGION" \
  --filters Name=tag:Name,Values="$NAME_TAG" Name=instance-state-name,Values=pending,running \
  --query 'Reservations[0].Instances[0].InstanceId' --output text 2>/dev/null || echo None)"

if [[ "$INSTANCE_ID" == "None" ]]; then
  USER_DATA="$(cat <<'EOF'
#!/bin/bash
set -euo pipefail
apt-get update -y
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
usermod -aG docker ubuntu
EOF
)"
  INSTANCE_ID="$(aws ec2 run-instances --region "$REGION" \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --metadata-options 'HttpTokens=required,HttpEndpoint=enabled' \
    --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=${VOLUME_GB},VolumeType=gp3,DeleteOnTermination=true}" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${NAME_TAG}},{Key=project,Value=peter-pan},{Key=stage,Value=A}]" \
    --user-data "$USER_DATA" \
    --query 'Instances[0].InstanceId' --output text)"
  log "Launched ${INSTANCE_ID} (${INSTANCE_TYPE})"
else
  log "Reusing running instance ${INSTANCE_ID}"
fi

aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"
PUBLIC_IP="$(aws ec2 describe-instances --region "$REGION" --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)"

log "READY instance=${INSTANCE_ID} public_ip=${PUBLIC_IP}"
echo "$PUBLIC_IP"
