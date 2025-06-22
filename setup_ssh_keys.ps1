# SSH Key Setup Script for GitHub Actions Deployment
# Run this in PowerShell on your local Windows machine

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  SSH Key Setup for GitHub Actions" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Configuration
$VPS_HOST = "5.181.5.168"
$VPS_USER = "trader"
$KEY_NAME = "id_rsa_vps_deploy"

Write-Host "This script will help you set up SSH keys for automated deployment."
Write-Host "VPS Host: $VPS_HOST"
Write-Host "VPS User: $VPS_USER"
Write-Host ""

# Check if ssh-keygen exists
if (-not (Get-Command ssh-keygen -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: ssh-keygen not found." -ForegroundColor Red
    Write-Host "Please install OpenSSH client:" -ForegroundColor Red
    Write-Host "  Windows 10/11: Settings > Apps > Optional Features > OpenSSH Client" -ForegroundColor Yellow
    Write-Host "  Or download from: https://github.com/PowerShell/Win32-OpenSSH/releases" -ForegroundColor Yellow
    exit 1
}

# Create .ssh directory if it doesn't exist
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
}

# Generate SSH key pair
Write-Host "Step 1: Generating SSH key pair..." -ForegroundColor Cyan
$keyPath = "$sshDir\$KEY_NAME"

if (Test-Path $keyPath) {
    Write-Host "Warning: Key file $keyPath already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Exiting without generating new key."
        exit 1
    }
}

$date = Get-Date -Format "yyyyMMdd"
& ssh-keygen -t rsa -b 4096 -C "github-actions-deploy-$date" -f $keyPath -N '""'

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH key pair generated successfully!" -ForegroundColor Green
    Write-Host "   Private key: $keyPath"
    Write-Host "   Public key: $keyPath.pub"
} else {
    Write-Host "❌ Failed to generate SSH key pair." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Public key content (copy this to your VPS):" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Yellow
Get-Content "$keyPath.pub"
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 3: Private key content for GitHub secrets:" -ForegroundColor Cyan
Write-Host "Copy the following content to GitHub repository secrets as 'VPS_SSH_KEY':" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow
Get-Content $keyPath
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 4: VPS Configuration Commands:" -ForegroundColor Cyan
Write-Host "Run these commands on your Windows VPS:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host "mkdir C:\Users\$VPS_USER\.ssh"
Write-Host "# Then add the public key content to:"
Write-Host "# C:\Users\$VPS_USER\.ssh\authorized_keys"
Write-Host "# You can use notepad to create this file:"
Write-Host "# notepad C:\Users\$VPS_USER\.ssh\authorized_keys"
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 5: Test SSH connection:" -ForegroundColor Cyan
Write-Host "ssh -i $keyPath $VPS_USER@$VPS_HOST" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 6: GitHub Repository Secrets:" -ForegroundColor Cyan
Write-Host "Go to your GitHub repository > Settings > Secrets and variables > Actions" -ForegroundColor Yellow
Write-Host "Add a new secret:" -ForegroundColor Yellow
Write-Host "  Name: VPS_SSH_KEY" -ForegroundColor Yellow
Write-Host "  Value: [paste the private key content from above]" -ForegroundColor Yellow
Write-Host ""

Write-Host "Setup complete! Test the SSH connection before pushing to main branch." -ForegroundColor Green

# Ask if user wants to test SSH connection now
Write-Host ""
$testNow = Read-Host "Do you want to test the SSH connection now? (y/n)"
if ($testNow -eq "y") {
    Write-Host "Testing SSH connection..." -ForegroundColor Cyan
    & ssh -i $keyPath -o ConnectTimeout=10 "$VPS_USER@$VPS_HOST" "echo 'SSH connection successful'"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSH connection test successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ SSH connection test failed." -ForegroundColor Red
        Write-Host "Make sure you've added the public key to the VPS authorized_keys file." -ForegroundColor Yellow
    }
}
