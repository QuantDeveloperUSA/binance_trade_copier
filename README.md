# Binance Copy Trading System

A simple Binance-to-Binance copy trading system that copies futures trades from master accounts to slave accounts.

## Features

- Real-time trade copying via WebSocket
- Balance-based position sizing with multiplier support
- Web interface for account management
- Trade history logging
- Support for up to 20 slave accounts

## Quick Start

1. **Install Python 3.12** (if not already installed)

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**
   - Double-click `Run_Server.bat` OR
   - Run: `python main.py`

4. **Access Web Interface**
   - Open browser: http://localhost:8000
   - Default accounts are pre-configured

## Initial Setup

The system comes with two pre-configured accounts:
- **Master Account**: master_1 (with provided API credentials)
- **Slave Account**: slave_1 (with provided API credentials)

## Usage

1. **Start Copy Trading**
   - Click "Start Copying" button in the web interface
   - Master trades will be automatically copied to slaves

2. **Add New Accounts**
   - Click "Add Account" button
   - Enter account details and API credentials
   - Choose account type (Master/Slave)
   - Set multiplier for slave accounts

3. **Monitor Trades**
   - View real-time trade logs in the interface
   - Check account balances and connection status

## Configuration

Edit `config.py` to adjust:
- API rate limits
- Logging level
- File paths

## File Structure

```
project/
├── main.py              # Main application
├── config.py            # Configuration
├── templates/
│   └── index.html       # Web interface
├── data/                # JSON storage
│   ├── accounts.json    # Account data
│   ├── trades.json      # Trade history
│   └── system.json      # System state
├── requirements.txt     # Python dependencies
├── Run_Server.bat       # Windows launcher
└── README.md           # This file
```

## Important Notes

- This system uses Binance Futures API
- Ensure API keys have futures trading permissions
- Monitor API rate limits to avoid bans
- Test with small amounts first

## Troubleshooting

1. **Connection Issues**
   - Verify API keys are correct
   - Check if API has futures permissions
   - Ensure internet connection is stable

2. **Trade Not Copying**
   - Verify master account is actively trading
   - Check slave account has sufficient balance
   - Review trade logs for errors

3. **Rate Limit Errors**
   - Reduce number of active slaves
   - Increase API_RATE_LIMIT_DELAY in config.py

## Security

- API keys are stored locally in JSON files
- No external database or cloud storage
- Keep your data folder secure

## Support

For issues or questions:
1. Check trade logs for error messages
2. Verify all API permissions are correct
3. Ensure sufficient balance in accounts
