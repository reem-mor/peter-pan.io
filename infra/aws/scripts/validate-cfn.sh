#!/usr/bin/env bash
# validate-cfn.sh — validate the PETER PAN CloudFormation template.
#
# Runs two checks:
#   1. cfn-lint  (offline structural/schema linting)
#   2. aws cloudformation validate-template  (API syntax check)
#
# Usage:
#   bash infra/aws/scripts/validate-cfn.sh
#   REGION=eu-west-1 bash infra/aws/scripts/validate-cfn.sh
#   AWS_PROFILE=demo bash infra/aws/scripts/validate-cfn.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="${TEMPLATE_PATH:-${SCRIPT_DIR}/../template.yaml}"
REGION="${REGION:-us-east-1}"

EXIT_CODE=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
header()  { printf '\n\033[36m=== %s ===\033[0m\n' "$*"; }
pass()    { printf '  \033[32mPASS\033[0m  %s\n' "$*"; }
fail()    { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; EXIT_CODE=1; }
warn()    { printf '  \033[33mWARN\033[0m  %s\n' "$*"; }

# ---------------------------------------------------------------------------
# Pre-flight
# ---------------------------------------------------------------------------
TEMPLATE="$(realpath "$TEMPLATE")"
printf 'Template : %s\n' "$TEMPLATE"
printf 'Region   : %s\n' "$REGION"
if [[ -n "${AWS_PROFILE:-}" ]]; then
    printf 'Profile  : %s\n' "$AWS_PROFILE"
fi

if [[ ! -f "$TEMPLATE" ]]; then
    fail "Template file not found: $TEMPLATE"
    exit 1
fi

# ---------------------------------------------------------------------------
# Check 1: cfn-lint
# ---------------------------------------------------------------------------
header "cfn-lint (structural / schema)"

if ! command -v cfn-lint &>/dev/null; then
    fail "cfn-lint not found. Install with: pip install cfn-lint"
else
    printf '  cfn-lint version: %s\n' "$(cfn-lint --version 2>&1)"

    if cfn-lint "$TEMPLATE" --format parseable 2>&1; then
        pass "cfn-lint — no issues found"
    else
        fail "cfn-lint found issues (see output above)"
    fi
fi

# ---------------------------------------------------------------------------
# Check 2: aws cloudformation validate-template
# ---------------------------------------------------------------------------
header "aws cloudformation validate-template (API)"

if ! command -v aws &>/dev/null; then
    fail "aws CLI not found. Install from: https://aws.amazon.com/cli/"
else
    printf '  AWS CLI version: %s\n' "$(aws --version 2>&1)"

    VALIDATE_OUT=$(aws cloudformation validate-template \
        --template-body "file://${TEMPLATE}" \
        --region "$REGION" 2>&1) && VALIDATE_EXIT=0 || VALIDATE_EXIT=$?

    if [[ $VALIDATE_EXIT -eq 0 ]]; then
        pass "validate-template — template is valid"
    else
        fail "validate-template failed"
        printf '%s\n' "$VALIDATE_OUT" | sed 's/^/    /'

        if echo "$VALIDATE_OUT" | grep -qiE 'NoCredentials|UnableToLocate|ExpiredToken'; then
            warn "AWS credentials not configured or expired."
            warn "Fix: aws configure  OR  export AWS_PROFILE=demo"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
header "Summary"
if [[ $EXIT_CODE -eq 0 ]]; then
    printf '\033[32m  All checks passed. Template is ready to deploy.\033[0m\n'
else
    printf '\033[31m  One or more checks failed. Fix issues before deploying.\033[0m\n'
fi

exit $EXIT_CODE
