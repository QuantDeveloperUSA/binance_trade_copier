# GitHub Actions Deployment Setup Instructions

## Overview
This repository is configured with GitHub Actions to automatically deploy the Binance Trade Copier to your Windows VPS whenever you push to the main branch.

## Prerequisites Setup

### 1. VPS Preparation
Run the setup script on your Windows VPS as Administrator:
```cmd
# Copy vps_setup.bat to your VPS and run:
vps_setup.bat
```

### 2. SSH Key Setup

#### Option A: Using existing SSH connection
If you're already connecting with username/password, you need to set up SSH key authentication:

1. **On your local machine**, generate an SSH key pair:
```bash
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy"
# Save as: id_rsa_vps_deploy (or any name you prefer)
# Leave passphrase empty for automation
```

2. **Copy the public key to your VPS**:
```bash
# Copy the content of id_rsa_vps_deploy.pub
cat ~/.ssh/id_rsa_vps_deploy.pub

# Then on your VPS, create the .ssh directory and authorized_keys file:
mkdir C:\Users\trader\.ssh
# Add the public key content to: C:\Users\trader\.ssh\authorized_keys
```

#### Option B: Generate keys on VPS
1. **On your VPS**, install OpenSSH if not already installed
2. Generate keys and configure:
```cmd
# Run on VPS
ssh-keygen -t rsa -b 4096
# Copy the public key to authorized_keys
copy C:\Users\trader\.ssh\id_rsa.pub C:\Users\trader\.ssh\authorized_keys
```

### 3. GitHub Repository Secrets Configuration

In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add:

#### Required Secrets:
- **`VPS_SSH_KEY`**: Your private SSH key content (entire content of id_rsa_vps_deploy or id_rsa file)

#### Optional Secrets (if you want to customize):
- **`VPS_HOST`**: Your VPS IP (default: 5.181.5.168)
- **`VPS_USER`**: Your VPS username (default: trader)
- **`DEPLOY_PATH`**: Deployment path on VPS (default: C:/trade_copier)

### 4. Test SSH Connection
Before deploying, test the SSH connection:
```bash
ssh -i ~/.ssh/id_rsa_vps_deploy trader@5.181.5.168
```

## Deployment Process

### Automatic Deployment
The deployment will trigger automatically when you:
- Push to the `main` branch
- Create a pull request that merges to `main`

### Manual Deployment
You can also trigger deployment manually:
1. Go to **Actions** tab in your GitHub repository
2. Select **Deploy to Windows VPS** workflow
3. Click **Run workflow**

## Deployment Steps

The GitHub Action performs these steps:
1. **Backup**: Creates backup of current deployment
2. **Stop Service**: Stops running application/service
3. **Deploy Files**: Transfers updated code to VPS
4. **Install Dependencies**: Updates Python packages
5. **Start Application**: Restarts the service/application
6. **Health Check**: Verifies deployment success

## Monitoring Deployment

### GitHub Actions
- Check the **Actions** tab for deployment status
- View detailed logs for each deployment step

### VPS Monitoring
After deployment, you can check:
```cmd
# Check if service is running
sc query BinanceTradeCopiersvc

# Check running processes
tasklist | findstr python.exe

# View application logs
type C:\trade_copier\binance_trade_copier.log

# Test web interface
curl http://localhost:8000/health
```

## Troubleshooting

### Common Issues:

1. **SSH Connection Failed**
   - Verify SSH key is correctly added to GitHub secrets
   - Test SSH connection manually
   - Check VPS firewall settings

2. **Permission Denied**
   - Ensure user 'trader' has write permissions to deployment directory
   - Run vps_setup.bat as Administrator

3. **Python/Pip Issues**
   - Verify Python is installed and in PATH on VPS
   - Check Python version compatibility (3.8+)

4. **Service Start Failed**
   - Check if Windows Service was created properly
   - View Windows Event Logs for service errors
   - Try manual start: `python C:\trade_copier\main.py`

5. **Dependencies Installation Failed**
   - Check internet connection on VPS
   - Verify pip is working: `python -m pip --version`
   - Check requirements.txt format

### Rollback Process
If deployment fails, the previous version is backed up:
```cmd
# On VPS, restore from backup:
cd C:\trade_copier
xcopy backup\*.* . /y
```

## Security Notes

- SSH private key is stored securely in GitHub secrets
- Never commit SSH keys or passwords to the repository
- Consider using GitHub environment protection rules for production
- Regularly rotate SSH keys
- Monitor deployment logs for security issues

## Customization

### Deployment Path
To change the deployment path, update the `DEPLOY_PATH` environment variable in `.github/workflows/deploy.yml`

### Service Configuration
Modify the `SERVICE_NAME` in the workflow file if you use a different service name

### Health Check Endpoint
The deployment verifies success using `/health` endpoint. Ensure this endpoint exists in your FastAPI application.

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. Verify VPS setup using vps_setup.bat
3. Test SSH connection manually
4. Check VPS system logs and application logs
