import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException
import uvicorn

from config import (
    DATA_DIR, ACCOUNTS_FILE, TRADES_FILE, SYSTEM_FILE,
    API_RATE_LIMIT_DELAY, LOG_LEVEL
)

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('binance_trade_copier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Binance Trade Copier")
templates = Jinja2Templates(directory="templates")

# Health check endpoint for deployment verification
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for deployment verification"""
    return {
        "status": "healthy",
        "service": "Binance Trade Copier",
        "timestamp": datetime.now().isoformat(),
        "copying_active": copying_active,
        "active_connections": len(active_connections)
    }

# Global variables
active_connections: Dict[str, AsyncClient] = {}
socket_managers: Dict[str, BinanceSocketManager] = {}
copying_active = False
master_positions: Dict[str, Dict] = {}

# Pydantic models
class Account(BaseModel):
    id: str
    type: str  # "master" or "slave"
    api_key: str
    api_secret: str
    multiplier: float = 1.0
    active: bool = True

class TradeRecord(BaseModel):
    timestamp: str
    master_id: str
    slave_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    error: Optional[str] = None

# File operations
def ensure_data_files():
    """Ensure all required data files exist"""
    DATA_DIR.mkdir(exist_ok=True)
    
    if not ACCOUNTS_FILE.exists():
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump({"accounts": []}, f, indent=2)
    
    if not TRADES_FILE.exists():
        with open(TRADES_FILE, 'w') as f:
            json.dump({"trades": []}, f, indent=2)
    
    if not SYSTEM_FILE.exists():
        with open(SYSTEM_FILE, 'w') as f:
            json.dump({"copying_active": False, "started_at": None}, f, indent=2)

def load_accounts() -> List[Dict]:
    """Load accounts from JSON file"""
    with open(ACCOUNTS_FILE, 'r') as f:
        data = json.load(f)
    return data.get('accounts', [])

def save_accounts(accounts: List[Dict]):
    """Save accounts to JSON file"""
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump({"accounts": accounts}, f, indent=2)

def save_trade(trade_data: Dict):
    """Save trade record to JSON file"""
    with open(TRADES_FILE, 'r+') as f:
        trades = json.load(f)
        trades['trades'].append(trade_data)
        # Keep only last 1000 trades
        trades['trades'] = trades['trades'][-1000:]
        f.seek(0)
        f.truncate()
        json.dump(trades, f, indent=2)

def update_system_state(copying: bool):
    """Update system state"""
    with open(SYSTEM_FILE, 'w') as f:
        json.dump({
            "copying_active": copying,
            "started_at": datetime.now().isoformat() if copying else None
        }, f, indent=2)

# Trading functions
async def get_account_balance(client: AsyncClient) -> float:
    """Get futures account balance"""
    try:
        account_info = await client.futures_account()
        # Use totalWalletBalance for the total balance including unrealized PnL
        balance = float(account_info.get('totalWalletBalance', 0))
        # If totalWalletBalance is 0, try availableBalance
        if balance == 0:
            balance = float(account_info.get('availableBalance', 0))
        return balance
    except BinanceAPIException as e:
        if "restricted location" in str(e):
            raise Exception("Binance access restricted in your location")
        elif "Invalid API" in str(e):
            raise Exception("Invalid API key or secret")
        else:
            raise Exception(f"API Error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting account balance: {e}")
        raise

async def get_account_history(client: AsyncClient, account_type: str) -> Dict:
    """Get comprehensive account history"""
    history = {
        "balance_history": [],
        "trade_history": [],
        "deposit_history": [],
        "withdraw_history": [],
        "positions": []
    }
    
    try:
        # Get current account info
        account_info = await client.futures_account()
        
        # Get balance info
        history["current_balance"] = {
            "total": float(account_info.get('totalWalletBalance', 0)),
            "available": float(account_info.get('availableBalance', 0)),
            "margin": float(account_info.get('totalMarginBalance', 0)),
            "unrealized_pnl": float(account_info.get('totalUnrealizedProfit', 0))
        }
        
        # Get open positions
        positions = account_info.get('positions', [])
        for pos in positions:
            if float(pos.get('positionAmt', 0)) != 0:
                history["positions"].append({
                    "symbol": pos.get('symbol'),
                    "amount": float(pos.get('positionAmt', 0)),
                    "entry_price": float(pos.get('entryPrice', 0)),
                    "mark_price": float(pos.get('markPrice', 0)),
                    "pnl": float(pos.get('unrealizedProfit', 0)),
                    "side": "LONG" if float(pos.get('positionAmt', 0)) > 0 else "SHORT"
                })
        
        # Get recent trades (last 7 days)
        try:
            trades = await client.futures_account_trades(limit=100)
            for trade in trades:
                history["trade_history"].append({
                    "time": datetime.fromtimestamp(trade['time'] / 1000).isoformat(),
                    "symbol": trade['symbol'],
                    "side": trade['side'],
                    "price": float(trade['price']),
                    "qty": float(trade['qty']),
                    "commission": float(trade['commission']),
                    "realized_pnl": float(trade.get('realizedPnl', 0))
                })
        except Exception as e:
            logger.error(f"Error fetching trade history: {e}")
        
        # Get deposit/withdraw history (spot wallet)
        try:
            # Check spot deposit history
            deposits = await client.get_deposit_history()
            if deposits:
                for dep in deposits:
                    history["deposit_history"].append({
                        "time": datetime.fromtimestamp(dep['insertTime'] / 1000).isoformat(),
                        "coin": dep['coin'],
                        "amount": float(dep['amount']),
                        "status": dep['status']
                    })
        except Exception as e:
            logger.error(f"Error fetching deposit history: {e}")
        
        # Get income history (funding fees, commissions, etc.)
        try:
            income = await client.futures_income_history(limit=100)
            for inc in income:
                if inc['incomeType'] == 'FUNDING_FEE':
                    history["trade_history"].append({
                        "time": datetime.fromtimestamp(inc['time'] / 1000).isoformat(),
                        "symbol": inc['symbol'],
                        "side": "FUNDING",
                        "price": 0,
                        "qty": 0,
                        "commission": float(inc['income']),
                        "realized_pnl": 0
                    })
        except Exception as e:
            logger.error(f"Error fetching income history: {e}")
            
    except Exception as e:
        logger.error(f"Error getting account history: {e}")
        raise
    
    return history

async def copy_to_slaves(trade_data: Dict, master_id: str):
    """Copy master trade to all active slaves"""
    if trade_data['e'] != 'ORDER_TRADE_UPDATE':
        return
    
    order_data = trade_data['o']
    if order_data['X'] != 'FILLED':
        return
    
    symbol = order_data['s']
    side = order_data['S']
    quantity = float(order_data['q'])
    price = float(order_data['ap'])
    
    logger.info(f"Master {master_id} executed: {side} {quantity} {symbol} @ {price}")
    
    # Get master balance
    master_client = active_connections.get(master_id)
    if not master_client:
        return
    
    master_balance = await get_account_balance(master_client)
    
    # Copy to each slave
    accounts = load_accounts()
    slaves = [acc for acc in accounts if acc['type'] == 'slave' and acc['active']]
    
    for slave in slaves:
        slave_id = slave['id']
        slave_client = active_connections.get(slave_id)
        
        if not slave_client:
            continue
        
        try:
            # Calculate slave quantity using the correct function signature
            slave_qty = await calculate_slave_quantity(
                slave, quantity, symbol, slave_client
            )
            
            if slave_qty <= 0:
                logger.warning(f"Skipping trade for slave {slave_id}: calculated quantity is 0")
                continue
            
            # Place slave order
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': slave_qty
            }
            
            # Check position mode for the slave
            position_mode = await slave_client.futures_get_position_mode()
            if position_mode.get('dualSidePosition', False):
                # In hedge mode, need to specify position side
                order_params['positionSide'] = 'LONG' if side == 'BUY' else 'SHORT'
            
            order = await slave_client.futures_create_order(**order_params)
            
            # Record successful trade
            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "master_id": master_id,
                "slave_id": slave_id,
                "symbol": symbol,
                "side": side,
                "quantity": slave_qty,
                "price": float(order.get('avgPrice', price)),
                "status": "success",
                "error": None
            }
            save_trade(trade_record)
            logger.info(f"Slave {slave_id} copied: {side} {slave_qty} {symbol}")
            
        except BinanceAPIException as e:
            # Record failed trade
            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "master_id": master_id,
                "slave_id": slave_id,
                "symbol": symbol,
                "side": side,
                "quantity": slave_qty if 'slave_qty' in locals() else 0,
                "price": price,
                "status": "failed",
                "error": str(e)
            }
            save_trade(trade_record)
            logger.error(f"Failed to copy trade to slave {slave_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error copying to slave {slave_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Rate limit delay
        await asyncio.sleep(API_RATE_LIMIT_DELAY)

async def monitor_master(master_id: str, api_key: str, api_secret: str):
    """Monitor master account for trades"""
    global copying_active
    
    try:
        client = await AsyncClient.create(api_key, api_secret)
        active_connections[master_id] = client
        
        bm = BinanceSocketManager(client)
        socket_managers[master_id] = bm
        
        # Start user data stream
        async with bm.futures_user_socket() as stream:
            logger.info(f"Started monitoring master {master_id}")
            
            while copying_active:
                try:
                    msg = await asyncio.wait_for(stream.recv(), timeout=30)
                    await copy_to_slaves(msg, master_id)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in master stream {master_id}: {e}")
                    break
        
    except Exception as e:
        logger.error(f"Failed to connect master {master_id}: {e}")
    finally:
        if master_id in active_connections:
            await active_connections[master_id].close_connection()
            del active_connections[master_id]
        if master_id in socket_managers:
            del socket_managers[master_id]

async def connect_slave(slave_id: str, api_key: str, api_secret: str):
    """Connect slave account"""
    try:
        client = await AsyncClient.create(api_key, api_secret)
        active_connections[slave_id] = client
        logger.info(f"Connected slave {slave_id}")
    except Exception as e:
        logger.error(f"Failed to connect slave {slave_id}: {e}")

# Quantity calculation function
async def calculate_slave_quantity(slave_account: Dict, master_quantity: float, symbol: str, client: AsyncClient) -> float:
    """Calculate the appropriate quantity for a slave account based on risk management"""
    try:
        # Get slave account balance
        account_info = await client.futures_account()
        balance = float(account_info.get('totalWalletBalance', 0))
        
        # Get current price
        ticker = await client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        
        # Calculate position value
        master_position_value = master_quantity * current_price
        
        # Apply risk percentage
        risk_percentage = slave_account.get('risk_percentage', 1.0) / 100.0
        max_position_value = balance * risk_percentage
        
        # Calculate slave quantity
        if master_position_value > max_position_value:
            # Scale down to match risk limit
            slave_quantity = max_position_value / current_price
        else:
            # Use same quantity as master
            slave_quantity = master_quantity
        
        # Round to appropriate decimals (3 for most cryptos)
        slave_quantity = round(slave_quantity, 3)
        
        # Check minimum notional value (Binance minimum is $20)
        min_notional = 20.0
        if slave_quantity * current_price < min_notional:
            logger.warning(f"Calculated quantity {slave_quantity} is below minimum notional ${min_notional}")
            slave_quantity = round(min_notional / current_price * 1.1, 3)  # Add 10% buffer
        
        logger.info(f"Calculated slave quantity: {slave_quantity} (master: {master_quantity})")
        return slave_quantity
        
    except Exception as e:
        logger.error(f"Error calculating slave quantity: {e}")
        # Return 0 to skip this trade
        return 0

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    ensure_data_files()
    logger.info("Binance Trade Copier started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global copying_active
    copying_active = False
    
    # Close all connections
    for client in active_connections.values():
        await client.close_connection()
    
    logger.info("System shutdown complete")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/accounts")
async def get_accounts():
    """Get all accounts"""
    accounts = load_accounts()
    return {"accounts": accounts}

@app.post("/api/accounts")
async def add_account(account: Account):
    """Add new account"""
    accounts = load_accounts()
    
    # Check if ID already exists
    if any(acc['id'] == account.id for acc in accounts):
        raise HTTPException(status_code=400, detail="Account ID already exists")
    
    accounts.append(account.dict())
    save_accounts(accounts)
    
    return {"message": "Account added successfully"}

@app.delete("/api/accounts/{account_id}")
async def delete_account(account_id: str):
    """Delete account"""
    accounts = load_accounts()
    accounts = [acc for acc in accounts if acc['id'] != account_id]
    save_accounts(accounts)
    
    # Disconnect if connected
    if account_id in active_connections:
        await active_connections[account_id].close_connection()
        del active_connections[account_id]
    
    return {"message": "Account deleted successfully"}

@app.post("/api/start")
async def start_copying():
    """Start copy trading"""
    global copying_active
    
    if copying_active:
        return {"message": "Copying already active"}
    
    copying_active = True
    update_system_state(True)
    
    accounts = load_accounts()
    masters = [acc for acc in accounts if acc['type'] == 'master' and acc['active']]
    slaves = [acc for acc in accounts if acc['type'] == 'slave' and acc['active']]
    
    # Connect slaves first
    for slave in slaves:
        asyncio.create_task(connect_slave(
            slave['id'], slave['api_key'], slave['api_secret']
        ))
    
    # Start monitoring masters
    for master in masters:
        asyncio.create_task(monitor_master(
            master['id'], master['api_key'], master['api_secret']
        ))
    
    return {"message": "Copy trading started"}

@app.post("/api/stop")
async def stop_copying():
    """Stop copy trading"""
    global copying_active
    
    copying_active = False
    update_system_state(False)
    
    # Connections will be closed by monitor tasks
    
    return {"message": "Copy trading stopped"}

@app.get("/api/status")
async def get_status():
    """Get system status"""
    with open(SYSTEM_FILE, 'r') as f:
        system_state = json.load(f)
    
    # Get connection status and balances
    connection_status = {}
    accounts = load_accounts()
    
    for account in accounts:
        account_id = account['id']
        
        # Check if already connected
        if account_id in active_connections:
            try:
                balance = await get_account_balance(active_connections[account_id])
                connection_status[account_id] = {
                    "connected": True,
                    "balance": balance
                }
            except Exception as e:
                connection_status[account_id] = {
                    "connected": False,
                    "balance": 0,
                    "error": str(e)
                }
        else:
            # Try to connect temporarily just to get balance
            try:
                # You can switch to testnet by uncommenting the next line
                # client = await AsyncClient.create(account['api_key'], account['api_secret'], testnet=True)
                temp_client = await AsyncClient.create(account['api_key'], account['api_secret'])
                balance = await get_account_balance(temp_client)
                await temp_client.close_connection()
                
                connection_status[account_id] = {
                    "connected": False,  # Not persistently connected
                    "balance": balance,
                    "available": True
                }
            except Exception as e:
                error_msg = str(e)
                if "restricted location" in error_msg:
                    error_msg = "Location restricted - Use VPN or Binance.US"
                elif "Invalid API" in error_msg:
                    error_msg = "Invalid API credentials"
                
                logger.error(f"Failed to get balance for {account_id}: {e}")
                connection_status[account_id] = {
                    "connected": False,
                    "balance": 0,
                    "error": error_msg
                }
    
    return {
        "copying_active": system_state['copying_active'],
        "started_at": system_state['started_at'],
        "connections": connection_status
    }

@app.get("/api/trades")
async def get_trades(limit: int = 100):
    """Get recent trades"""
    with open(TRADES_FILE, 'r') as f:
        trades = json.load(f)
    
    recent_trades = trades['trades'][-limit:]
    return {"trades": recent_trades}

@app.get("/api/accounts/{account_id}/history")
async def get_account_history_endpoint(account_id: str):
    """Get account history for a specific account"""
    accounts = load_accounts()
    account = next((acc for acc in accounts if acc['id'] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        # Create temporary client if not connected
        if account_id in active_connections:
            client = active_connections[account_id]
        else:
            client = await AsyncClient.create(account['api_key'], account['api_secret'])
        
        history = await get_account_history(client, account['type'])
        
        # Close temporary client
        if account_id not in active_connections:
            await client.close_connection()
        
        return history
    except Exception as e:
        logger.error(f"Error getting history for {account_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts/{account_id}/balance")
async def get_account_balance_endpoint(account_id: str):
    """Get detailed balance for a specific account"""
    accounts = load_accounts()
    account = next((acc for acc in accounts if acc['id'] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        # Create temporary client if not connected
        if account_id in active_connections:
            client = active_connections[account_id]
        else:
            client = await AsyncClient.create(account['api_key'], account['api_secret'])
        
        account_info = await client.futures_account()
        
        balance_details = {
            "total_wallet": float(account_info.get('totalWalletBalance', 0)),
            "available": float(account_info.get('availableBalance', 0)),
            "total_margin": float(account_info.get('totalMarginBalance', 0)),
            "unrealized_pnl": float(account_info.get('totalUnrealizedProfit', 0)),
            "assets": []
        }
        
        # Get individual asset balances
        for asset in account_info.get('assets', []):
            if float(asset.get('walletBalance', 0)) > 0:
                balance_details["assets"].append({
                    "asset": asset['asset'],
                    "wallet_balance": float(asset['walletBalance']),
                    "unrealized_pnl": float(asset.get('unrealizedProfit', 0))
                })
        
        # Close temporary client
        if account_id not in active_connections:
            await client.close_connection()
        
        return balance_details
    except Exception as e:
        logger.error(f"Error getting balance for {account_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    try:
        logger.info("=" * 50)
        logger.info("STARTING BINANCE TRADE COPIER APPLICATION")
        logger.info("=" * 50)
        logger.info("Initializing application...")
        
        # Verify data directory exists
        if not DATA_DIR.exists():
            logger.info(f"Creating data directory: {DATA_DIR}")
            DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Check if data files exist
        for file_path, default_content in [
            (ACCOUNTS_FILE, "{}"),
            (TRADES_FILE, "[]"),
            (SYSTEM_FILE, '{"copying_active": false}')
        ]:
            if not file_path.exists():
                logger.info(f"Creating default file: {file_path}")
                file_path.write_text(default_content)
        
        logger.info("Data files verified")
        logger.info(f"Server starting on http://0.0.0.0:8000")
        logger.info("Health endpoint: http://0.0.0.0:8000/health")
        logger.info("Web interface: http://0.0.0.0:8000")
        logger.info("=" * 50)
        
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        logger.error(f"CRITICAL ERROR: Failed to start application: {e}")
        logger.error("Check the error details above")
        import traceback
        logger.error(traceback.format_exc())
        input("Press Enter to exit...")  # Keep console open to see error
        raise
