from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL, ENCRYPTION_KEY
from cryptography.fernet import Fernet

Base = declarative_base()
# Configure connection pool with proper settings
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_size=20,  # Increase pool size
    max_overflow=40,  # Allow more overflow connections
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600  # Recycle connections after 1 hour
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

fernet = Fernet(ENCRYPTION_KEY)

class Account(Base):  # type: ignore
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_type = Column(String, nullable=False)  # 'master' or 'slave'
    account_mode = Column(String, default="spot")  # 'spot' or 'futures'
    name = Column(String, nullable=False)
    api_key_encrypted = Column(String, nullable=False)
    api_secret_encrypted = Column(String, nullable=False)
    balance_multiplier = Column(Float, default=1.0)
    fixed_ratio = Column(Float, nullable=True)  # For fixed copy ratio mode
    is_active = Column(Boolean, default=True)
    master_account_id = Column(Integer, nullable=True)  # For slave accounts
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Risk management settings
    max_position_size = Column(Float, nullable=True)  # Max position size limit
    risk_percentage = Column(Float, default=2.0)  # Risk percentage per trade
    
    def set_api_key(self, api_key: str) -> None:
        encrypted_key = fernet.encrypt(api_key.encode()).decode()
        self.api_key_encrypted = encrypted_key  # type: ignore
    
    def get_api_key(self) -> str:
        encrypted_key: str = self.api_key_encrypted  # type: ignore
        return fernet.decrypt(encrypted_key.encode()).decode()
    
    def set_api_secret(self, api_secret: str) -> None:
        encrypted_secret = fernet.encrypt(api_secret.encode()).decode()
        self.api_secret_encrypted = encrypted_secret  # type: ignore
    
    def get_api_secret(self) -> str:
        encrypted_secret: str = self.api_secret_encrypted  # type: ignore
        return fernet.decrypt(encrypted_secret.encode()).decode()

class Trade(Base):  # type: ignore
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    master_trade_id = Column(String, nullable=False)
    master_account_id = Column(Integer, nullable=False)  # Track master account
    slave_account_id = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY or SELL
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    order_type = Column(String, default="MARKET")  # MARKET, LIMIT, etc.
    status = Column(String, nullable=False)  # SUCCESS, FAILED, PENDING
    error_message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    binance_order_id = Column(String, nullable=True)
    
    # Additional trade info
    commission = Column(Float, nullable=True)
    commission_asset = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
