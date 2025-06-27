import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from binance import AsyncClient
from binance.exceptions import BinanceAPIException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"

async def check_slave_account(slave_id: str = None):
    
    with open(ACCOUNTS_FILE, 'r') as f:
        data = json.load(f)
    
    slave_accounts = [acc for acc in data['accounts'] if acc['type'] == 'slave']
    
    if not slave_accounts:
        logger.error("No slave accounts found!")
        return
    
    if slave_id:
        slave_account = next((acc for acc in slave_accounts if acc['id'] == slave_id), None)
        if not slave_account:
            logger.error(f"Slave account {slave_id} not found!")
            return
        slave_accounts = [slave_account]
    
    for slave in slave_accounts:
        logger.info("=" * 60)
        logger.info(f"Checking slave account: {slave['id']}")
        logger.info("=" * 60)
        
        client = None
        try:
            logger.info("Connecting to Binance...")
            client = await AsyncClient.create(
                slave['api_key'], 
                slave['api_secret']
            )
            
            logger.info("\n📊 ACCOUNT INFORMATION")
            account_info = await client.futures_account()
            
            logger.info("\n💰 BALANCES:")
            logger.info(f"Total Wallet Balance: ${float(account_info.get('totalWalletBalance', 0)):.2f}")
            logger.info(f"Available Balance: ${float(account_info.get('availableBalance', 0)):.2f}")
            logger.info(f"Total Margin Balance: ${float(account_info.get('totalMarginBalance', 0)):.2f}")
            logger.info(f"Total Unrealized PnL: ${float(account_info.get('totalUnrealizedProfit', 0)):.2f}")
            
            logger.info("\n💎 ASSET BREAKDOWN:")
            assets = account_info.get('assets', [])
            for asset in assets:
                wallet_balance = float(asset.get('walletBalance', 0))
                if wallet_balance > 0:
                    logger.info(f"{asset['asset']}: {wallet_balance:.4f} (${float(asset.get('marginBalance', 0)):.2f})")
            
            logger.info("\n📈 OPEN POSITIONS:")
            positions = account_info.get('positions', [])
            has_positions = False
            for pos in positions:
                position_amt = float(pos.get('positionAmt', 0))
                if position_amt != 0:
                    has_positions = True
                    logger.info(f"Symbol: {pos['symbol']}")
                    logger.info(f"  Amount: {position_amt}")
                    logger.info(f"  Entry Price: ${float(pos.get('entryPrice', 0)):.2f}")
                    logger.info(f"  Mark Price: ${float(pos.get('markPrice', 0)):.2f}")
                    logger.info(f"  Unrealized PnL: ${float(pos.get('unrealizedProfit', 0)):.2f}")
                    logger.info(f"  Side: {'LONG' if position_amt > 0 else 'SHORT'}")
            
            if not has_positions:
                logger.info("No open positions")
            
            logger.info("\n📜 RECENT TRADES (Last 10):")
            try:
                trades = await client.futures_account_trades(limit=10)
                if trades:
                    for trade in trades:
                        trade_time = datetime.fromtimestamp(trade['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        logger.info(f"{trade_time}: {trade['side']} {float(trade['qty'])} {trade['symbol']} @ ${float(trade['price']):.2f}")
                        if float(trade.get('realizedPnl', 0)) != 0:
                            logger.info(f"  Realized PnL: ${float(trade['realizedPnl']):.2f}")
                else:
                    logger.info("No recent trades found")
            except Exception as e:
                logger.error(f"Error fetching trades: {e}")
            
            logger.info("\n📋 RECENT ORDERS (Last 5):")
            try:
                orders = await client.futures_get_all_orders(symbol='ETHUSDT', limit=5)
                if orders:
                    for order in orders:
                        order_time = datetime.fromtimestamp(order['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        logger.info(f"{order_time}: {order['side']} {order['type']} {float(order['origQty'])} {order['symbol']}")
                        logger.info(f"  Status: {order['status']}")
                        if order['status'] == 'FILLED':
                            logger.info(f"  Avg Price: ${float(order.get('avgPrice', 0)):.2f}")
                else:
                    logger.info("No recent orders found")
            except Exception as e:
                logger.error(f"Error fetching orders: {e}")
            
            logger.info("\n⚙️ ACCOUNT STATUS:")
            logger.info(f"Can Trade: {account_info.get('canTrade', False)}")
            logger.info(f"Can Withdraw: {account_info.get('canWithdraw', False)}")
            logger.info(f"Can Deposit: {account_info.get('canDeposit', False)}")
            
            try:
                spot_account = await client.get_account()
                logger.info("\n🔍 ACCOUNT TYPE: LIVE (Production)")
            except Exception as e:
                if "testnet" in str(e).lower():
                    logger.info("\n🔍 ACCOUNT TYPE: TESTNET")
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Error: {e}")
            if "restricted location" in str(e):
                logger.error("⚠️  Your location is restricted. Use a VPN or Binance.US")
            elif "Invalid API" in str(e):
                logger.error("⚠️  Invalid API key or secret")
            elif "-2015" in str(e):
                logger.error("⚠️  Invalid API-key, IP, or permissions for action")
                logger.error("   Check that your API key has futures trading enabled")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            if client:
                await client.close_connection()
                logger.info("\nConnection closed")

async def main():
    logger.info("=" * 60)
    logger.info("BINANCE SLAVE ACCOUNT CHECK")
    logger.info("=" * 60)
    
    with open(ACCOUNTS_FILE, 'r') as f:
        data = json.load(f)
    
    slave_accounts = [acc for acc in data['accounts'] if acc['type'] == 'slave']
    
    if not slave_accounts:
        logger.error("No slave accounts found in accounts.json!")
        return
    
    logger.info("\nAvailable slave accounts:")
    for i, slave in enumerate(slave_accounts, 1):
        logger.info(f"{i}. {slave['id']} (Active: {slave.get('active', True)})")
    
    choice = input("\nEnter slave account number (or 'all' to check all): ")
    
    if choice.lower() == 'all':
        await check_slave_account()
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(slave_accounts):
                await check_slave_account(slave_accounts[idx]['id'])
            else:
                logger.error("Invalid selection")
        except ValueError:
            logger.error("Invalid input")

if __name__ == "__main__":
    asyncio.run(main())
