# Binance Trade Copier - Auto Deployment Guide

This document explains how to set up auto-deployment from GitHub to your Windows VPS using GitHub Actions.

## Prerequisites

1. **VPS Setup**: Windows Server 2022 Standard with SSH access
2. **Local Setup**: Windows 11 with VS Code and GitHub Copilot
3. **Repository**: GitHub repository with this code

## VPS Requirements

Your VPS should have:
- SSH Server configured and running
- Python 3.8+ installed
- Git installed
- Access to trader@5.181.5.168

## GitHub Secrets Configuration

You need to configure the following secrets in your GitHub repository:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following **Repository secrets**:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `VPS_HOST` | `5.181.5.168` | Your VPS IP address |
| `VPS_USERNAME` | `trader` | SSH username |
| `SSH_PRIVATE_KEY` | `your_private_key_content` | SSH private key for authentication |

### How to Add Secrets:
1. Click **"New repository secret"**
2. Enter the **Name** (e.g., `VPS_HOST`)
3. Enter the **Secret** value
4. Click **"Add secret"**

## SSH Key Setup

### 1. Generate SSH Key Pair (on your local machine)
```cmd
ssh-keygen -t rsa -b 4096 -C "trader@5.181.5.168"
```
- When prompted for file location, press Enter (default: `C:\Users\your_user\.ssh\id_rsa`)
- When prompted for passphrase, press Enter for no passphrase (recommended for automation)

### 2. Copy Public Key to VPS
```cmd
# Copy the public key content
type C:\Users\your_user\.ssh\id_rsa.pub
```

Then on your VPS:
```cmd
# SSH to your VPS
ssh trader@5.181.5.168

# Create .ssh directory if it doesn't exist
mkdir C:\Users\trader\.ssh

# Add your public key to authorized_keys
echo your_public_key_content >> C:\Users\trader\.ssh\authorized_keys
```

### 3. Add Private Key to GitHub Secrets
```cmd
# Get your private key content (on local machine)
type C:\Users\your_user\.ssh\id_rsa
```
Copy the entire content (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`) and add it as the `SSH_PRIVATE_KEY` secret in GitHub.

## VPS Initial Setup

Before the first deployment, prepare your VPS:

### 1. Connect to VPS via SSH
```cmd
ssh trader@5.181.5.168
```

### 2. Install Required Software
```cmd
# Install Python (if not already installed)
# Download from https://www.python.org/downloads/windows/

# Install Git (if not already installed)
# Download from https://git-scm.com/download/win

# Verify installations
python --version
git --version
pip --version
```

### 3. Create Deployment Directory
```cmd
mkdir C:\Users\trader\binance_trade_copier
cd C:\Users\trader\binance_trade_copier
```

### 4. Configure Git (First time only)
```cmd
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## GitHub Repository Setup

### 1. Update the Workflow File
The GitHub Actions workflow is already configured in `.github/workflows/deploy.yml`. You may need to update the Git repository URL:

```yaml
# In the workflow file, replace with your actual repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### 2. Required Files
Make sure your repository has:
- `main.py` - Main application file
- `requirements.txt` - Python dependencies
- `config.py` - Configuration file
- `templates/` - HTML templates directory
- `.github/workflows/deploy.yml` - Deployment workflow

## Deployment Process

### Automatic Deployment
Every time you push to the `main` branch, the deployment will automatically:

1. **Stop** existing application processes
2. **Backup** existing data files
3. **Update** code from GitHub
4. **Install** Python dependencies
5. **Start** the application
6. **Verify** deployment success

### Manual Deployment
You can also trigger deployment manually:

1. Go to your GitHub repository
2. Navigate to **Actions** tab
3. Select **"Deploy Binance Trade Copier to Windows VPS"**
4. Click **"Run workflow"**

## Monitoring Deployment

### Check Deployment Status
1. Go to **Actions** tab in your GitHub repository
2. View the latest workflow run
3. Check logs for any errors

### Verify Application
After deployment, verify the application is running:

```cmd
# SSH to your VPS
ssh trader@5.181.5.168

# Check if application is running
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Binance Trade Copier",
  "timestamp": "2025-06-22T...",
  "copying_active": false,
  "active_connections": 0
}
```

### View Application Logs
```cmd
# On your VPS
cd C:\Users\trader\binance_trade_copier
type app.log
```

## Troubleshooting

### Common Issues

#### 1. SSH Connection Failed
- Verify VPS IP address and credentials
- Check if SSH service is running on VPS
- Ensure firewall allows SSH connections

#### 2. Git Clone/Pull Failed
- Verify repository URL in workflow
- Check if Git is installed on VPS
- Ensure VPS has internet access

#### 3. Python Dependencies Failed
- Check if Python is installed and in PATH
- Verify pip is working: `pip --version`
- Check internet connectivity for package downloads

#### 4. Application Start Failed
- Check application logs: `type app.log`
- Verify all required files are present
- Check for port conflicts (default port 8000)

### Debug Commands

```cmd
# Check running Python processes
tasklist | findstr python

# Check if port 8000 is in use
netstat -an | findstr :8000

# View recent application logs
type app.log | more

# Check deployment directory
dir C:\Users\trader\binance_trade_copier
```

## Security Notes

1. **SSH Keys**: Consider using SSH keys instead of passwords for better security
2. **Secrets**: Never commit secrets to your repository
3. **Firewall**: Configure Windows Firewall to allow only necessary ports
4. **Updates**: Keep your VPS and applications updated

## Application Access

After successful deployment, your application will be available at:
- **Health Check**: `http://your-vps-ip:8000/health`
- **Main Application**: `http://your-vps-ip:8000`

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. Review VPS application logs
3. Verify all prerequisites are met
4. Test SSH connection manually
