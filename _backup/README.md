# Binance Copy Trading System

A professional-grade automated copy trading system for Binance that replicates trades from master accounts to multiple slave accounts in real-time. Built with Python, FastAPI, and WebSocket technology for reliable trade execution.

## ✨ Features

### Core Trading Features
- **Real-time Trade Copying**: Instant replication via Binance WebSocket streams
- **Multiple Position Sizing Options**:
  - Balance-based proportional sizing
  - Fixed ratio multipliers
  - Custom balance multipliers per slave account
- **Exchange Support**: 
  - Binance Global (binance.com)
  - Binance US (binance.us)
- **Trade Types**: Market orders with immediate execution
- **Error Handling**: Comprehensive error logging and automatic reconnection

### Account Management
- **Master/Slave Architecture**: One master can control multiple slave accounts
- **Account Status Control**: Enable/disable accounts individually
- **Encrypted API Storage**: Secure API key/secret encryption using Fernet
- **Balance Monitoring**: Automatic periodic balance updates

### User Interface
- **Web Dashboard**: Modern responsive interface at `http://localhost:8000`
- **Real-time Updates**: Live trade history and account status
- **Account Management**: Add, edit, delete, and toggle accounts
- **Trade History**: Detailed logs with status tracking
- **System Status**: Monitor active connections and performance

### Deployment Options
- **Standalone Application**: Run directly with Python
- **Windows Service**: Auto-start on system boot
- **Executable Build**: Single-file deployment with PyInstaller
- **VPS Ready**: Complete deployment package for remote servers

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Binance API keys with trading permissions
- Windows OS (for service installation)

### Installation

1. **Clone and Install**
```bash
git clone <repository-url>
cd joseph_binance_trade_copier
pip install -r requirements.txt
```

2. **Generate Encryption Key**
```bash
python generate_key.py
```
Copy the generated key to `config.py` replacing `ENCRYPTION_KEY`

3. **Configure Exchange**
Edit `config.py`:
```python
# For Binance Global
BINANCE_EXCHANGE = "global"

# For Binance US  
BINANCE_EXCHANGE = "us"
```

4. **Start the Application**
```bash
python main.py
# OR
run.bat
```

5. **Access Web Interface**
Open `http://localhost:8000` and login with password: `admin123`

## 📋 Configuration

### Environment Setup
Key configuration options in `config.py`:

```python
# Security
ADMIN_PASSWORD = "admin123"  # Change in production
ENCRYPTION_KEY = b"your-generated-key"

# Exchange Selection
BINANCE_EXCHANGE = "global"  # or "us"

# Performance Tuning
BALANCE_UPDATE_INTERVAL = 300  # seconds
WEBSOCKET_RECONNECT_DELAY = 5  # seconds
DEFAULT_MULTIPLIER = 1.0
```

### API Key Requirements
- **Spot Trading**: Enable spot trading permissions
- **No Withdrawals**: Disable withdrawal permissions for security
- **IP Restrictions**: Recommended for additional security

## 💼 Usage Guide

### Setting Up Accounts

1. **Add Master Account**:
   - Account Type: Master
   - Name: Descriptive name
   - API Key: Binance API key
   - API Secret: Binance API secret

2. **Add Slave Accounts**:
   - Account Type: Slave
   - Master Account: Select the master to follow
   - Balance Multiplier: Proportion of master's trade size
   - Fixed Ratio: Optional fixed multiplier (overrides balance-based)

### Position Sizing Examples

**Balance-based Sizing**:
- Master balance: $10,000, trades $1,000 (10%)
- Slave balance: $5,000, multiplier: 1.0
- Slave trade size: $500 (10% of $5,000)

**Fixed Ratio Sizing**:
- Master trades $1,000
- Slave fixed ratio: 0.5
- Slave trade size: $500 (regardless of balance)

## 🛠 Advanced Deployment

### Windows Service Installation

1. **Build Executable**:
```bash
build_exe.bat
```

2. **Install as Service**:
```bash
python service_installer.py
```

3. **Service Management**:
```bash
# Start service
net start BinanceCopyTrader

# Stop service  
net stop BinanceCopyTrader

# Check status
sc query BinanceCopyTrader
```

### VPS Deployment

1. **Create Deployment Package**:
```bash
deploy_to_vps.bat
```

2. **Transfer to VPS**: Copy the `deployment` folder to your VPS

3. **Install on VPS**: Run as Administrator:
```bash
python service_installer.py
```

## 📊 Monitoring & Logs

### Log Files
- **Application Logs**: `trade_copier.log`
- **Trade History**: Stored in SQLite database
- **Error Tracking**: Detailed error messages and stack traces

### Web Dashboard Features
- **Account Overview**: Balance, status, multipliers
- **Trade History**: Recent trades with status
- **System Status**: Active connections, performance metrics
- **Real-time Updates**: Live data refresh

## 🔧 Development

### Type Checking
Run comprehensive type checks:
```bash
check_types.bat
```

This generates reports in the `reports/` folder:
- `pyright_report.txt` - TypeScript-style type checking
- `mypy_report.txt` - Python type checking  
- `pylint_report.txt` - Code quality analysis

### Project Structure
```
joseph_binance_trade_copier/
├── main.py                 # FastAPI application
├── database.py             # SQLAlchemy models
├── config.py               # Configuration settings
├── templates/              # Web UI templates
├── service_wrapper.py      # Windows service wrapper
├── service_installer.py    # Service installation script
├── generate_key.py         # Encryption key generator
├── build_exe.bat          # Executable builder
├── deploy_to_vps.bat      # VPS deployment packager
└── requirements.txt        # Python dependencies
```

## 🔐 Security Best Practices

### API Key Security
- **Restrict Permissions**: Only enable spot trading
- **IP Whitelisting**: Restrict API access to your IPs
- **Regular Rotation**: Change API keys periodically
- **Environment Variables**: Use environment variables in production

### Application Security
- **Change Default Password**: Update `ADMIN_PASSWORD` in config
- **Generate New Encryption Key**: Use `generate_key.py` for production
- **Secure Hosting**: Use HTTPS in production environments
- **Network Security**: Firewall rules for port 8000

## 🚨 Risk Warnings

- **Trading Risks**: All trading involves risk of financial loss
- **API Limits**: Monitor Binance API rate limits
- **Network Dependencies**: Ensure stable internet connection
- **Testing Required**: Test with small amounts before full deployment
- **Backup Important**: Keep secure backups of encryption keys

## 📈 Performance Notes

- **WebSocket Efficiency**: Direct connection to Binance streams
- **Async Processing**: Non-blocking trade execution
- **Auto Reconnection**: Handles network interruptions
- **Balance Caching**: Reduces API calls with periodic updates
- **Error Recovery**: Graceful handling of API errors

## 🐛 Troubleshooting

### Common Issues

**Service Won't Start**:
- Check Windows Event Viewer
- Verify file permissions
- Ensure Python dependencies are installed

**Trades Not Copying**:
- Verify WebSocket connection in logs
- Check master account API permissions
- Confirm account is active and enabled

**API Errors**:
- Verify API key permissions
- Check Binance server status
- Review rate limiting

### Support
Check log files for detailed error messages and stack traces. All errors are logged with timestamps for debugging.

## 📄 License

This project is for educational and personal use. Please ensure compliance with Binance Terms of Service and local regulations.

---

**⚠️ Disclaimer**: This software is provided as-is. Users are responsible for testing, risk management, and compliance with all applicable regulations. The authors are not responsible for any financial losses.
