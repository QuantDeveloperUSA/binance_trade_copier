from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Data files
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
TRADES_FILE = DATA_DIR / "trades.json"
SYSTEM_FILE = DATA_DIR / "system.json"

# API settings
API_RATE_LIMIT_DELAY = 0.1  # Delay between API calls in seconds

# Logging
LOG_LEVEL = "INFO"

# Web interface
WEB_PASSWORD = "admin123"  # Basic password protection
