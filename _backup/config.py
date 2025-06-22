import os
from pathlib import Path

# Generate a key for encryption (run once and save)
# print(Fernet.generate_key())

# Encryption key - CHANGE THIS IN PRODUCTION
# This is a valid example key - DO NOT USE IN PRODUCTION
ENCRYPTION_KEY = b'y2YACc9ZqiTJNW8y9G9E3-k0jdXGVm7THLuXfOfRAvY='  # Must be 44 chars base64

# Application data directory (Windows AppData)
APP_NAME = "BinanceCopyTrader"
APP_DATA_DIR = Path(os.environ.get('LOCALAPPDATA', '')) / APP_NAME
APP_DATA_DIR.mkdir(exist_ok=True)

# Create subdirectories
DATA_DIR = APP_DATA_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR = APP_DATA_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DATA_DIR / 'trade_copier.db'}"

# Binance API limits
MAX_WEIGHT_PER_MINUTE = 1200
MAX_ORDERS_PER_10_SECONDS = 50

# Simple auth (change in production)
ADMIN_PASSWORD = "admin123"

# Binance Exchange Selection
# Set to "global" for binance.com or "us" for binance.us
BINANCE_EXCHANGE = "global"  # Changed to global for futures support

# Add account type configuration
DEFAULT_ACCOUNT_MODE = "futures"  # Changed to futures as default

# Binance Endpoints (automatically set based on BINANCE_EXCHANGE)
# These are the default endpoints used by python-binance
BINANCE_ENDPOINTS = {
    "global": {
        "base": "https://api.binance.com",
        "stream": "wss://stream.binance.com:9443",
        "futures": "https://fapi.binance.com",
        "futures_stream": "wss://fstream.binance.com"
    },
    "us": {
        "base": "https://api.binance.us",
        "stream": "wss://stream.binance.us:9443",
        "futures": None,  # Binance US doesn't support futures
        "futures_stream": None
    }
}

# Feature Availability by Exchange
EXCHANGE_FEATURES = {
    "global": {
        "spot": True,
        "futures": True,
        "margin": True,
        "savings": True,
        "staking": True,
        "options": True
    },
    "us": {
        "spot": True,
        "futures": False,  # Not available
        "margin": True,     # Limited pairs
        "savings": True,    # Limited products
        "staking": True,    # Limited coins
        "options": False    # Not available
    }
}

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = str(LOGS_DIR / "trade_copier.log")  # Creates a logs folder  # This creates trade_copier.log in current directory

# WebSocket settings
WEBSOCKET_RECONNECT_DELAY = 5  # seconds
WEBSOCKET_HEARTBEAT_INTERVAL = 30  # seconds

# Trading settings
DEFAULT_MULTIPLIER = 1.0
BALANCE_UPDATE_INTERVAL = 30  # seconds
MAX_SLAVE_ACCOUNTS = 20  # Maximum slaves per master
MIN_ORDER_VALUE = 10.0  # Minimum order value in USDT

# Risk Management
DEFAULT_RISK_PERCENTAGE = 2.0  # Default risk per trade
MAX_POSITION_SIZE_RATIO = 0.95  # Max 95% of balance
STOP_LOSS_PERCENTAGE = 2.0  # Default stop loss

# Rate Limiting
API_CALLS_PER_SECOND = 10
WEBSOCKET_PING_INTERVAL = 20  # seconds

# Error Handling
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds between retries
