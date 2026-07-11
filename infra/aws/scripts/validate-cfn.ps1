<#
.SYNOPSIS
  Validates the PETER PAN CloudFormation template using cfn-lint and the AWS CLI.

.DESCRIPTION
  Runs two checks:
    1. cfn-lint  — structural/schema linting (offline, no AWS calls)
    2. aws cloudformation validate-template  — API-side syntax check (requires AWS creds)

  Both checks must pass before deploying.

.PARAMETER TemplatePath
  Path to the CloudFormation template. Defaults to ../template.yaml relative to this script.

.PARAMETER Region
  AWS region for the validate-template API call. Defaults to us-east-1.

.PARAMETER Profile
  AWS CLI profile. Leave blank to use the default credential chain.

.EXAMPLE
  .\validate-cfn.ps1
  .\validate-cfn.ps1 -TemplatePath C:\dev\peter-pan.io\infra\aws\template.yaml -Region eu-west-1

#>
[CmdletBinding()]
param(
    [string]$TemplatePath = (Join-Path $PSScriptRoot "..\template.yaml"),
    [string]$Region       = "us-east-1",
    [string]$Profile      = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Write-Header([string]$Text) {
    Write-Host "`n=== $Text ===" -ForegroundColor Cyan
}

function Write-Pass([string]$Text) {
    Write-Host "  PASS  $Text" -ForegroundColor Green
}

function Write-Fail([string]$Text) {
    Write-Host "  FAIL  $Text" -ForegroundColor Red
}

$AwsArgs = @()
if ($Profile) { $AwsArgs += "--profile", $Profile }

$ExitCode = 0

# ---------------------------------------------------------------------------
# Pre-flight: resolve template path
# ---------------------------------------------------------------------------
$TemplatePath = Resolve-Path $TemplatePath -ErrorAction Stop | Select-Object -ExpandProperty Path
Write-Host "Template : $TemplatePath"
Write-Host "Region   : $Region"
if ($Profile) { Write-Host "Profile  : $Profile" }

# ---------------------------------------------------------------------------
# Check 1: cfn-lint
# ---------------------------------------------------------------------------
Write-Header "cfn-lint (structural / schema)"

$CfnLint = Get-Command cfn-lint -ErrorAction SilentlyContinue
if (-not $CfnLint) {
    Write-Fail "cfn-lint not found. Install with: pip install cfn-lint"
    $ExitCode = 1
} else {
    Write-Host "  cfn-lint version: $(cfn-lint --version 2>&1)"

    $LintOutput = cfn-lint $TemplatePath --format parseable 2>&1
    $LintExit   = $LASTEXITCODE

    if ($LintExit -eq 0) {
        Write-Pass "cfn-lint — no issues found"
    } else {
        Write-Fail "cfn-lint found issues:"
        $LintOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
        $ExitCode = 1
    }
}

# ---------------------------------------------------------------------------
# Check 2: aws cloudformation validate-template
# ---------------------------------------------------------------------------
Write-Header "aws cloudformation validate-template (API)"

$AwsCli = Get-Command aws -ErrorAction SilentlyContinue
if (-not $AwsCli) {
    Write-Fail "aws CLI not found. Install from: https://aws.amazon.com/cli/"
    $ExitCode = 1
} else {
    Write-Host "  AWS CLI version: $(aws --version 2>&1)"

    $ValidateArgs = @(
        "cloudformation", "validate-template",
        "--template-body", "file://$TemplatePath",
        "--region", $Region
    ) + $AwsArgs

    $ValidateOutput = & aws @ValidateArgs 2>&1
    $ValidateExit   = $LASTEXITCODE

    if ($ValidateExit -eq 0) {
        Write-Pass "validate-template — template is valid"
    } else {
        Write-Fail "validate-template failed:"
        $ValidateOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }

        if ($ValidateOutput -match "NoCredentialsError|UnableToLocateCredentials|ExpiredToken") {
            Write-Host "`n  TIP: Configure AWS credentials with:" -ForegroundColor DarkYellow
            Write-Host "       aws sso login --profile demo" -ForegroundColor DarkYellow
            Write-Host "       then set AWS_PROFILE=demo" -ForegroundColor DarkYellow
        }
        $ExitCode = 1
    }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Header "Summary"
if ($ExitCode -eq 0) {
    Write-Host "  All checks passed. Template is ready to deploy." -ForegroundColor Green
} else {
    Write-Host "  One or more checks failed. Fix issues before deploying." -ForegroundColor Red
}

exit $ExitCode
