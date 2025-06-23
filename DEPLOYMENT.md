# Deployment Guide

## GitHub Actions Automatic Deployment

This repository is set up with GitHub Actions to automatically deploy to your Windows VPS whenever you push to the main/master branch.

### Required GitHub Secrets

Make sure you have the following secrets configured in your GitHub repository settings:

- `VPS_HOST`: Your VPS IP address (5.181.5.168)
- `VPS_USER`: Your VPS username (trader)  
- `VPS_PASSWORD`: Your VPS password (encrypted)

### How it Works

1. **Trigger**: The deployment runs automatically when you push to main/master branch, or you can trigger it manually
2. **Stop existing**: Any running instance of the application is stopped
3. **File copy**: All necessary files are copied to `C:\binance_copier\` on your VPS
4. **Dependencies**: Python dependencies are installed/updated from requirements.txt
5. **Start app**: The application is started with `python main.py`
6. **Verification**: The deployment is verified by checking the process and health endpoint

### Manual Deployment (Alternative)

If you need to deploy manually, you can also:

1. Copy all files to your VPS at `C:\binance_copier\`
2. Run `deploy.bat` or `deploy.ps1` on the VPS

### Monitoring

The GitHub Action will show you:
- ✅ Successful deployment and application startup
- 🔍 Process verification 
- 🌐 Health check results (if available)
- 📊 Application logs (if there are errors)

### Application Management

**Check if running:**
```powershell
Get-Process -Name python | Where-Object { $_.CommandLine -like "*main.py*" }
```

**Stop the application:**
```powershell
Get-Process -Name python | Where-Object { $_.CommandLine -like "*main.py*" } | Stop-Process -Force
```

**Start manually:**
```powershell
cd C:\binance_copier
python main.py
```

### Troubleshooting

If deployment fails:

1. **Check Python**: Ensure Python is installed and in PATH on your VPS
2. **Check permissions**: Ensure the `trader` user has access to `C:\binance_copier\`
3. **Check logs**: Look at the GitHub Actions logs for detailed error messages
4. **Check application logs**: Check `binance_trade_copier.log` on the VPS

### Application Access

- **Health endpoint**: http://your-vps-ip:8000/health
- **Web interface**: http://your-vps-ip:8000 (if configured)
- **Logs**: `C:\binance_copier\binance_trade_copier.log`

The deployment is designed to be simple and effective - just push your code and it will be automatically deployed and started on your VPS!
