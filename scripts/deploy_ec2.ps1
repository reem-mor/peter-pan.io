# Deploy PETER PAN to EC2 (Windows wrapper around SCP + remote bash script).
param(
    [string]$IP = "18.234.123.139",
    [string]$KeyFile = "$env:USERPROFILE\.ssh\peter-pan-key.pem"
)
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Tar = Join-Path $env:TEMP "peter-pan-deploy.tgz"
Write-Output ">>> Packaging working tree..."
& git ls-files -co --exclude-standard -z | & tar -czf $Tar --null -T -
Write-Output ">>> SCP to ubuntu@${IP}..."
& scp -i $KeyFile -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 $Tar "ubuntu@${IP}:/tmp/peter-pan.tgz"
& scp -i $KeyFile -o StrictHostKeyChecking=accept-new "$RepoRoot\scripts\remote_deploy_ec2.sh" "ubuntu@${IP}:/tmp/remote_deploy_ec2.sh"
Write-Output ">>> Remote deploy..."
& ssh -i $KeyFile -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 "ubuntu@$IP" "chmod +x /tmp/remote_deploy_ec2.sh && bash /tmp/remote_deploy_ec2.sh"
Remove-Item -Force $Tar -ErrorAction SilentlyContinue
Write-Output ">>> DEPLOYED to ${IP}"
