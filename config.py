from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

ACCOUNTS_FILE = DATA_DIR / "accounts.json"
TRADES_FILE = DATA_DIR / "trades.json"
SYSTEM_FILE = DATA_DIR / "system.json"

API_RATE_LIMIT_DELAY = 0.1

LOG_LEVEL = "INFO"

WEB_PASSWORD = "admin123"
