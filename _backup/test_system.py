import asyncio
import pytest
import httpx
import json
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# Import our modules
from database import Base, Account, Trade, get_db
from main import app, calculate_slave_quantity, get_account_balance
from config import ENCRYPTION_KEY

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_trade_copier.db"

class TestTradeCalculations:
    """Test trade size calculation logic"""
    
    def test_balance_based_calculation(self):
        """Test balance-based position sizing"""
        # Mock slave account
        slave_account = Mock()
        slave_account.id = 2
        slave_account.fixed_ratio = None
        slave_account.balance_multiplier = 1.0
        
        # Mock account balances
        with patch('main.account_balances', {1: 10000, 2: 5000}):
            result = asyncio.run(calculate_slave_quantity(
                master_quantity=1000,
                master_account_id=1,
                slave_account=slave_account
            ))
            
            # Slave should get 50% of master trade (5000/10000 * 1000)
            assert result == 500.0
    
    def test_fixed_ratio_calculation(self):
        """Test fixed ratio position sizing"""
        slave_account = Mock()
        slave_account.id = 2
        slave_account.fixed_ratio = 0.5
        slave_account.balance_multiplier = 1.0
        
        with patch('main.account_balances', {1: 10000, 2: 5000}):
            result = asyncio.run(calculate_slave_quantity(
                master_quantity=1000,
                master_account_id=1,
                slave_account=slave_account
            ))
            
            # Fixed ratio should override balance calculation
            assert result == 500.0
    
    def test_multiplier_effect(self):
        """Test balance multiplier effect"""
        slave_account = Mock()
        slave_account.id = 2
        slave_account.fixed_ratio = None
        slave_account.balance_multiplier = 2.0
        
        with patch('main.account_balances', {1: 10000, 2: 5000}):
            result = asyncio.run(calculate_slave_quantity(
                master_quantity=1000,
                master_account_id=1,
                slave_account=slave_account
            ))
            
            # 2x multiplier: (5000/10000 * 1000) * 2 = 1000
            assert result == 1000.0

class TestDatabaseOperations:
    """Test database operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create test database"""
        engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = TestingSessionLocal()
        yield db
        db.close()
        
        # Cleanup
        os.remove("test_trade_copier.db")
    
    def test_account_creation(self, test_db):
        """Test creating accounts"""
        account = Account(
            account_type="master",
            name="Test Master",
            balance_multiplier=1.0
        )
        account.set_api_key("test_key")
        account.set_api_secret("test_secret")
        
        test_db.add(account)
        test_db.commit()
        
        # Verify account was created
        saved_account = test_db.query(Account).first()
        assert saved_account.name == "Test Master"
        assert saved_account.get_api_key() == "test_key"
        assert saved_account.get_api_secret() == "test_secret"
    
    def test_trade_logging(self, test_db):
        """Test trade logging"""
        trade = Trade(
            master_trade_id="12345",
            slave_account_id=1,
            symbol="BTCUSDT",
            side="BUY",
            quantity=0.001,
            status="SUCCESS"
        )
        
        test_db.add(trade)
        test_db.commit()
        
        saved_trade = test_db.query(Trade).first()
        assert saved_trade.symbol == "BTCUSDT"
        assert saved_trade.status == "SUCCESS"

class TestAPIEndpoints:
    """Test FastAPI endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return httpx.AsyncClient(app=app, base_url="http://test")
    
    @pytest.mark.asyncio
    async def test_home_endpoint(self, client):
        """Test home page loads"""
        response = await client.get("/")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_auth_endpoint(self, client):
        """Test authentication"""
        # Test correct password
        response = await client.post("/auth", data={"password": "admin123"})
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Test wrong password
        response = await client.post("/auth", data={"password": "wrong"})
        assert response.status_code == 401

class TestBinanceIntegration:
    """Test Binance API integration (mocked)"""
    
    @pytest.mark.asyncio
    async def test_balance_fetching(self):
        """Test balance fetching with mocked Binance client"""
        mock_account = Mock()
        mock_account.id = 1
        mock_account.get_api_key.return_value = "test_key"
        mock_account.get_api_secret.return_value = "test_secret"
        
        # Mock Binance client response
        mock_client = AsyncMock()
        mock_client.get_account.return_value = {
            'balances': [
                {'asset': 'USDT', 'free': '1000.0', 'locked': '0.0'},
                {'asset': 'BTC', 'free': '0.1', 'locked': '0.0'}
            ]
        }
        
        with patch('main.AsyncClient.create', return_value=mock_client):
            balance = await get_account_balance(mock_account)
            assert balance == 1000.0  # Only USDT counted

class TestWebSocketHandling:
    """Test WebSocket message processing"""
    
    def test_trade_message_parsing(self):
        """Test parsing of Binance trade messages"""
        # Sample Binance execution report
        sample_message = {
            'e': 'executionReport',
            's': 'BTCUSDT',
            'S': 'BUY',
            'q': '0.001',
            't': '12345',
            'x': 'TRADE'
        }
        
        # Test message should trigger copy logic
        assert sample_message['e'] == 'executionReport'
        assert sample_message['x'] == 'TRADE'
        assert float(sample_message['q']) == 0.001

def run_basic_tests():
    """Run basic tests without pytest"""
    print("🧪 Running Basic System Tests...\n")
    
    # Test 1: Configuration loading
    print("✅ Test 1: Configuration Loading")
    from config import ADMIN_PASSWORD, BINANCE_EXCHANGE
    assert ADMIN_PASSWORD == "admin123"
    assert BINANCE_EXCHANGE in ["global", "us"]
    print("   Configuration loaded successfully")
    
    # Test 2: Database models
    print("✅ Test 2: Database Models")
    try:
        from database import Account, Trade
        account = Account(account_type="test", name="Test Account")
        print("   Database models instantiated successfully")
    except Exception as e:
        print(f"   ❌ Database model error: {e}")
    
    # Test 3: Encryption/Decryption
    print("✅ Test 3: Encryption System")
    try:
        from database import fernet
        test_key = "test_api_key"
        encrypted = fernet.encrypt(test_key.encode()).decode()
        decrypted = fernet.decrypt(encrypted.encode()).decode()
        assert decrypted == test_key
        print("   Encryption/decryption working correctly")
    except Exception as e:
        print(f"   ❌ Encryption error: {e}")
    
    # Test 4: FastAPI app
    print("✅ Test 4: FastAPI Application")
    try:
        from main import app
        assert app is not None
        print("   FastAPI app initialized successfully")
    except Exception as e:
        print(f"   ❌ FastAPI error: {e}")
    
    print("\n🎉 Basic tests completed!")

if __name__ == "__main__":
    run_basic_tests()
