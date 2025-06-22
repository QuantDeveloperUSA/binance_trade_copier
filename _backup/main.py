import asyncio
import logging
from typing import Dict, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException

from database import get_db, Account, Trade, SessionLocal
from config import (
    ADMIN_PASSWORD, LOG_LEVEL, LOG_FILE, 
    WEBSOCKET_RECONNECT_DELAY, DEFAULT_MULTIPLIER,
    BALANCE_UPDATE_INTERVAL, BINANCE_EXCHANGE
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state
active_connections: Dict[int, asyncio.Task] = {}
account_balances: Dict[int, float] = {}
binance_clients: Dict[int, AsyncClient] = {}
connection_status: Dict[int, str] = {}  # Track actual connection status

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting trade copier...")
    # Start monitoring active master accounts
    db = next(get_db())
    masters = db.query(Account).filter(
        Account.account_type == "master",
        Account.is_active == True
    ).all()
    for master in masters:
        master_id: int = master.id  # type: ignore
        await start_monitoring(master_id)
    
    # Start balance update task
    balance_task = asyncio.create_task(update_balances())
    
    yield
    # Shutdown
    logger.info("Shutting down trade copier...")
    balance_task.cancel()
    for task in active_connections.values():
        task.cancel()
    for client in binance_clients.values():
        await client.close_connection()

app = FastAPI(lifespan=lifespan)

async def get_account_balance(account: Account) -> float:
    """Get account balance from Binance (supports both spot and futures)"""
    try:
        account_id: int = account.id  # type: ignore
        account_mode: str = account.account_mode or "spot"  # type: ignore
        
        # Get and validate API credentials
        api_key = account.get_api_key()
        api_secret = account.get_api_secret()
        
        # Basic validation of API key format
        if not api_key or not api_secret:
            logger.error(f"Missing API credentials for account {account_id}")
            connection_status[account_id] = "MISSING_CREDENTIALS"
            return account_balances.get(account_id, 0.0)
        
        if len(api_key.strip()) < 10 or len(api_secret.strip()) < 10:
            logger.error(f"Invalid API key format for account {account_id} - key too short")
            connection_status[account_id] = "INVALID_FORMAT"
            return account_balances.get(account_id, 0.0)
        
        if account_id not in binance_clients:
            binance_clients[account_id] = await AsyncClient.create(
                api_key.strip(),
                api_secret.strip(),
                tld='us' if BINANCE_EXCHANGE == 'us' else 'com',
                testnet=False
            )
        
        client = binance_clients[account_id]
        
        # Get balance based on account mode
        if account_mode == "futures":
            # Check if futures is available for the exchange
            if BINANCE_EXCHANGE == 'us':
                logger.error(f"Futures trading not available on Binance US for account {account_id}")
                connection_status[account_id] = "FUTURES_NOT_AVAILABLE"
                return 0.0
            
            # Get futures account balance
            futures_balance = await client.futures_account_balance()
            total_balance = 0.0
            
            for asset in futures_balance:
                if asset['asset'] == 'USDT':
                    total_balance = float(asset['balance'])
                    break
        else:
            # Get spot account balance (existing code)
            account_info = await client.get_account()
            
            # Calculate total balance in USDT
            total_balance = 0.0
            for balance in account_info['balances']:
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    if balance['asset'] == 'USDT':
                        total_balance += float(balance['free']) + float(balance['locked'])
        
        account_balances[account_id] = total_balance
        connection_status[account_id] = "CONNECTED"  # Mark as connected
        return total_balance
    except BinanceAPIException as e:
        account_id = account.id  # type: ignore
        error_msg = str(e)
        
        # Check for location restriction
        if "restricted location" in error_msg:
            logger.error(f"Location restricted for account {account_id}. You may need to use Binance US or a VPN.")
            connection_status[account_id] = "LOCATION_RESTRICTED"
        elif "API-key format invalid" in error_msg:
            logger.error(f"Invalid API key format for account {account_id}. Please check and update the API key.")
            connection_status[account_id] = "INVALID_API_KEY"
            # Remove the invalid client to force recreation on next attempt
            if account_id in binance_clients:
                try:
                    await binance_clients[account_id].close_connection()
                except:
                    pass
                del binance_clients[account_id]
        else:
            logger.error(f"Binance API error for account {account_id}: {e}")
            connection_status[account_id] = "API_ERROR"
        return account_balances.get(account_id, 0.0)
    except Exception as e:
        account_id = account.id  # type: ignore
        logger.error(f"Error fetching balance for account {account_id}: {e}")
        connection_status[account_id] = "CONNECTION_ERROR"
        return account_balances.get(account_id, 0.0)

async def update_balances():
    """Periodically update account balances"""
    while True:
        # Create a new session for this background task
        db = SessionLocal()
        try:
            accounts = db.query(Account).filter(Account.is_active == True).all()
            for account in accounts:
                await get_account_balance(account)
        finally:
            db.close()
        await asyncio.sleep(BALANCE_UPDATE_INTERVAL)

async def calculate_slave_quantity(
    master_quantity: float,
    master_account_id: int,
    slave_account: Account
) -> float:
    """Calculate position size for slave account"""
    master_balance = account_balances.get(master_account_id, 1.0)
    slave_id: int = slave_account.id  # type: ignore
    slave_balance = account_balances.get(slave_id, 1.0)
    
    fixed_ratio: Optional[float] = slave_account.fixed_ratio  # type: ignore
    if fixed_ratio:
        return master_quantity * fixed_ratio
    else:
        multiplier: float = slave_account.balance_multiplier or DEFAULT_MULTIPLIER  # type: ignore
        return float((master_quantity * slave_balance / master_balance) * multiplier)

async def execute_slave_trade(
    slave_account: Account,
    symbol: str,
    side: str,
    quantity: float,
    master_trade_id: str,
    db: Session
) -> Trade:
    """Execute trade on slave account (supports both spot and futures)"""
    trade = Trade(
        master_trade_id=master_trade_id,
        slave_account_id=slave_account.id,  # type: ignore
        symbol=symbol,
        side=side,
        quantity=quantity,
        status="PENDING"
    )
    
    try:
        slave_id: int = slave_account.id  # type: ignore
        account_mode: str = slave_account.account_mode or "spot"  # type: ignore
        
        if slave_id not in binance_clients:
            binance_clients[slave_id] = await AsyncClient.create(
                slave_account.get_api_key(),
                slave_account.get_api_secret(),
                tld='us' if BINANCE_EXCHANGE == 'us' else 'com'
            )
        
        client = binance_clients[slave_id]
        
        # Place order based on account mode
        if account_mode == "futures":
            # Place futures market order
            order = await client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
        else:
            # Place spot market order (existing code)
            order = await client.create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
        
        trade.status = "SUCCESS"  # type: ignore
        trade.binance_order_id = str(order['orderId'])  # type: ignore
        trade.price = float(order.get('fills', [{}])[0].get('price', 0)) if 'fills' in order else float(order.get('avgPrice', 0))  # type: ignore
        logger.info(f"Successfully copied trade to slave {slave_id}: {symbol} {side} {quantity}")
        
    except BinanceAPIException as e:
        trade.status = "FAILED"  # type: ignore
        trade.error_message = str(e)  # type: ignore
        logger.error(f"Failed to copy trade to slave {slave_account.id}: {e}")
    except Exception as e:
        trade.status = "FAILED"  # type: ignore
        trade.error_message = str(e)  # type: ignore
        logger.error(f"Unexpected error copying trade to slave {slave_account.id}: {e}")
    
    db.add(trade)
    db.commit()
    return trade

async def copy_to_slaves(master_id: int, trade_data: dict[str, Any]):
    """Copy master trade to all active slave accounts"""
    if trade_data.get('x') != 'TRADE':  # Only process filled trades
        return
    
    symbol = trade_data['s']
    side = trade_data['S']
    quantity = float(trade_data['q'])
    trade_id = str(trade_data['t'])
    
    logger.info(f"Master {master_id} executed: {symbol} {side} {quantity}")
    
    # Create a new session for this operation
    db = SessionLocal()
    try:
        slaves = db.query(Account).filter(
            Account.account_type == "slave",
            Account.master_account_id == master_id,
            Account.is_active == True
        ).all()
        
        tasks = []
        for slave in slaves:
            slave_quantity = await calculate_slave_quantity(quantity, master_id, slave)
            task = execute_slave_trade(slave, symbol, side, slave_quantity, trade_id, db)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    finally:
        db.close()

async def monitor_master(master_id: int):
    """Monitor master account for trades (supports both spot and futures)"""
    # Create a new session for this operation
    db = SessionLocal()
    try:
        master = db.query(Account).filter(Account.id == master_id).first()
        
        if not master:
            logger.error(f"Master account {master_id} not found")
            connection_status[master_id] = "NOT_FOUND"
            return
            
        # Copy needed data before closing session
        api_key = master.get_api_key()
        api_secret = master.get_api_secret()
        account_mode: str = master.account_mode or "spot"  # type: ignore
    finally:
        db.close()
    
    while True:
        try:
            if master_id not in binance_clients:
                binance_clients[master_id] = await AsyncClient.create(
                    api_key,
                    api_secret,
                    tld='us' if BINANCE_EXCHANGE == 'us' else 'com'
                )
            
            client = binance_clients[master_id]
            bm = BinanceSocketManager(client)
            
            logger.info(f"Starting WebSocket monitoring for {account_mode} master {master_id}")
            connection_status[master_id] = "MONITORING"  # Mark as actively monitoring
            
            # Use appropriate websocket based on account mode
            if account_mode == "futures":
                async with bm.futures_user_socket() as stream:
                    while True:
                        msg = await stream.recv()
                        if msg.get('e') == 'ORDER_TRADE_UPDATE':
                            # Convert futures message format to spot format
                            trade_data = {
                                'e': 'executionReport',
                                'x': 'TRADE' if msg['o']['X'] == 'FILLED' else msg['o']['X'],
                                's': msg['o']['s'],
                                'S': msg['o']['S'],
                                'q': msg['o']['q'],
                                't': msg['o']['t']
                            }
                            await copy_to_slaves(master_id, trade_data)
            else:
                # Spot trading websocket (existing code)
                async with bm.user_socket() as stream:
                    while True:
                        msg = await stream.recv()
                        if msg.get('e') == 'executionReport':
                            await copy_to_slaves(master_id, msg)
                        
        except Exception as e:
            logger.error(f"WebSocket error for master {master_id}: {e}")
            connection_status[master_id] = "WEBSOCKET_ERROR"
            await asyncio.sleep(WEBSOCKET_RECONNECT_DELAY)

async def start_monitoring(master_id: int):
    """Start monitoring a master account"""
    if master_id not in active_connections:
        task = asyncio.create_task(monitor_master(master_id))
        active_connections[master_id] = task
        # Also start balance monitoring
        db = SessionLocal()
        try:
            master = db.query(Account).filter(Account.id == master_id).first()
            if master:
                await get_account_balance(master)
        finally:
            db.close()

async def stop_monitoring(master_id: int):
    """Stop monitoring a master account"""
    if master_id in active_connections:
        active_connections[master_id].cancel()
        del active_connections[master_id]
    if master_id in binance_clients:
        await binance_clients[master_id].close_connection()
        del binance_clients[master_id]
    connection_status[master_id] = "STOPPED"  # Mark as stopped

# API Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth")
async def authenticate(password: str = Form(...)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"success": True}

@app.get("/api/accounts")
async def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return [{
        "id": acc.id,
        "type": acc.account_type,
        "mode": acc.account_mode or "spot",  # Add account mode
        "name": acc.name,
        "is_active": acc.is_active,
        "connection_status": connection_status.get(acc.id, "UNKNOWN"),  # Add real connection status
        "balance": account_balances.get(acc.id, 0.0),  # type: ignore
        "multiplier": acc.balance_multiplier,
        "fixed_ratio": acc.fixed_ratio,
        "master_id": acc.master_account_id
    } for acc in accounts]

@app.post("/api/accounts")
async def create_account(
    account_type: str = Form(...),
    account_mode: str = Form("spot"),  # Add account mode
    name: str = Form(...),
    api_key: str = Form(...),
    api_secret: str = Form(...),
    master_id: Optional[int] = Form(None),
    multiplier: float = Form(1.0),
    fixed_ratio: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    # Check if futures is available for the selected exchange
    if account_mode == "futures" and BINANCE_EXCHANGE == "us":
        raise HTTPException(
            status_code=400, 
            detail="Futures trading is not available on Binance US. Please use spot trading or switch to Binance Global."
        )
    
    account = Account(
        account_type=account_type,
        account_mode=account_mode,
        name=name,
        balance_multiplier=multiplier,
        fixed_ratio=fixed_ratio,
        master_account_id=master_id if account_type == "slave" else None
    )
    account.set_api_key(api_key)
    account.set_api_secret(api_secret)
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    # Start monitoring if master
    if account_type == "master":
        new_account_id: int = account.id  # type: ignore
        await start_monitoring(new_account_id)
    
    # Get initial balance
    await get_account_balance(account)
    
    return {"success": True, "id": account.id}

@app.post("/api/accounts/{account_id}/toggle")
async def toggle_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    current_active: bool = account.is_active  # type: ignore
    account.is_active = not current_active  # type: ignore
    db.commit()
    
    account_type: str = account.account_type  # type: ignore
    if account_type == "master":
        new_active: bool = account.is_active  # type: ignore
        if new_active:
            toggle_account_id: int = account.id  # type: ignore
            await start_monitoring(toggle_account_id)
        else:
            toggle_account_id: int = account.id  # type: ignore
            await stop_monitoring(toggle_account_id)
    
    return {"success": True, "is_active": account.is_active}

@app.delete("/api/accounts/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Delete an account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Stop monitoring if it's a master account
    account_type: str = account.account_type  # type: ignore
    if account_type == "master":
        await stop_monitoring(account_id)
    
    db.delete(account)
    db.commit()
    
    return {"success": True}

@app.put("/api/accounts/{account_id}")
async def update_account(
    account_id: int,
    multiplier: Optional[float] = Form(None),
    fixed_ratio: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """Update account settings"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if multiplier is not None:
        account.balance_multiplier = multiplier  # type: ignore
    if fixed_ratio is not None:
        account.fixed_ratio = fixed_ratio  # type: ignore
    
    db.commit()
    return {"success": True}

@app.get("/api/trades")
async def get_trades(limit: int = 50, db: Session = Depends(get_db)):
    trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
    return [{
        "id": t.id,
        "master_trade_id": t.master_trade_id,
        "slave_account_id": t.slave_account_id,
        "symbol": t.symbol,
        "side": t.side,
        "quantity": t.quantity,
        "price": t.price,
        "status": t.status,
        "error": t.error_message,
        "timestamp": t.timestamp.isoformat()  # type: ignore
    } for t in trades]

@app.get("/api/status")
async def get_system_status():
    """Get system status and statistics"""
    return {
        "active_masters": len(active_connections),
        "total_accounts": len(account_balances),
        "total_clients": len(binance_clients),
        "exchange": BINANCE_EXCHANGE
    }

@app.get("/api/binance-time")
async def get_binance_time():
    """Get Binance server time to test API connectivity"""
    try:
        # Use a public endpoint, no credentials needed
        client = await AsyncClient.create()
        server_time = await client.get_server_time()
        await client.close_connection()
        return {"time": server_time["serverTime"]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/connection-status/{account_id}")
async def check_connection_status(account_id: int, db: Session = Depends(get_db)):
    """Test Binance connection for a specific account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        # Force a balance check to test connection
        balance = await get_account_balance(account)
        status = connection_status.get(account_id, "UNKNOWN")
        return {
            "account_id": account_id,
            "status": status,
            "balance": balance,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "account_id": account_id,
            "status": "ERROR",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
