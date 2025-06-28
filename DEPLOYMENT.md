# Deployment Guide

This document explains the automated deployment system for the Binance Trade Copier application.

## Overview

The application uses GitHub Actions to automatically deploy the latest version of the main branch to the production Windows server whenever changes are pushed to the main branch.

## Components

### 1. GitHub Workflow (`.github/workflows/auto-pull-main.yml`)

The workflow file contains two main steps:
- **Deploy**: Executes the PowerShell deployment script on the Windows server via SSH
- **Verify**: Performs additional verification checks to ensure deployment success

### 2. PowerShell Deployment Script (`deploy.ps1`)

A comprehensive PowerShell script that handles:
- Git operations (fetch and reset to latest main branch)
- Process management (stopping old instances, starting new ones)
- Health checks and verification
- Error handling and logging

### 3. Test Script (`test_deployment.sh`)

A bash script that simulates the deployment process locally for testing purposes.

## How It Works

1. **Trigger**: When code is pushed to the main branch, GitHub Actions automatically triggers the workflow
2. **SSH Connection**: The workflow connects to the Windows production server using stored credentials
3. **Deployment Script**: Executes the PowerShell deployment script which:
   - Updates the codebase from git
   - Stops existing Python processes
   - Starts the new version of the application
   - Verifies the deployment was successful
4. **Verification**: Additional checks confirm the application is running and responding to health checks

## Configuration

### GitHub Secrets Required

The following secrets must be configured in the GitHub repository:

- `SERVER_HOST`: IP address or hostname of the Windows server
- `SERVER_USER`: Username for SSH connection
- `SERVER_SSH_KEY`: Private SSH key for authentication

### Server Requirements

The Windows server must have:
- SSH server enabled and configured
- Git installed and configured
- Python 3.12 installed
- PowerShell execution policy allowing script execution
- The repository cloned to `C:\binance_trade_copier`

## Manual Deployment

You can also run the deployment script manually on the server:

```powershell
# Basic deployment
powershell -ExecutionPolicy Bypass -File "C:\binance_trade_copier\deploy.ps1"

# Skip git operations (just restart the application)
powershell -ExecutionPolicy Bypass -File "C:\binance_trade_copier\deploy.ps1" -SkipGitPull

# Skip restart (just update code)
powershell -ExecutionPolicy Bypass -File "C:\binance_trade_copier\deploy.ps1" -SkipRestart

# Custom project path
powershell -ExecutionPolicy Bypass -File "C:\binance_trade_copier\deploy.ps1" -ProjectPath "D:\custom_path"
```

## Testing

To test the deployment logic locally (on Linux/macOS):

```bash
# Make the test script executable and run it
chmod +x test_deployment.sh
./test_deployment.sh
```

This creates a test environment and simulates the deployment process.

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   - Verify SERVER_HOST, SERVER_USER, and SERVER_SSH_KEY secrets are correct
   - Ensure SSH server is running on the Windows machine
   - Check firewall settings

2. **Git Operations Failed**
   - Ensure git is installed on the Windows server
   - Verify the repository exists at `C:\binance_trade_copier`
   - Check if there are uncommitted local changes blocking the reset

3. **Application Failed to Start**
   - Verify Python is installed and in the PATH
   - Check that all required dependencies are installed
   - Look for error messages in the deployment logs

4. **Health Check Failed**
   - Ensure the application is binding to `0.0.0.0:8000` (not just `localhost`)
   - Check Windows Firewall settings for port 8000
   - Verify no other process is using port 8000

### Viewing Logs

The deployment script provides detailed logging. You can also check:
- GitHub Actions logs for the deployment workflow
- Windows Event Viewer for system-level issues
- Application logs (`binance_trade_copier.log`)

## Security Considerations

- SSH keys should be properly secured and have limited permissions
- The deployment script only affects the specific project directory
- All sensitive credentials are stored as GitHub secrets, not in code
- The application runs with the permissions of the SSH user

## Monitoring

The deployment includes automatic health checks, but you should also monitor:
- Application logs for runtime errors
- Server performance and resource usage
- Trading activity to ensure the application is functioning correctly

## Rollback Procedure

If a deployment fails or introduces issues:

1. **Quick Rollback**: Use git to revert to a previous commit:
   ```powershell
   cd C:\binance_trade_copier
   git reset --hard <previous_commit_hash>
   powershell -ExecutionPolicy Bypass -File deploy.ps1 -SkipGitPull
   ```

2. **Manual Restart**: If just the application needs restarting:
   ```powershell
   powershell -ExecutionPolicy Bypass -File deploy.ps1 -SkipGitPull
   ```