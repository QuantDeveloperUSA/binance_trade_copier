import asyncio
import json
import logging
from pathlib import Path
from binance import AsyncClient
from binance.exceptions import BinanceAPIException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load account data
DATA_DIR = Path(__file__).parent / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"

async def test_buy_eth():
    """Test buying ETH on the master account"""
    
    # Load accounts
    with open(ACCOUNTS_FILE, 'r') as f:
        data = json.load(f)
    
    # Find master account
    master_account = None
    for account in data['accounts']:
        if account['type'] == 'master' and account['id'] == 'master_1':
            master_account = account
            break
    
    if not master_account:
        logger.error("Master account not found!")
        return
    
    logger.info(f"Using master account: {master_account['id']}")
    
    # Connect to Binance
    client = None
    try:
        logger.info("Connecting to Binance...")
        client = await AsyncClient.create(
            master_account['api_key'], 
            master_account['api_secret']
        )
        
        # Get account info to verify connection
        logger.info("Getting account balance...")
        account_info = await client.futures_account()
        balance = float(account_info.get('totalWalletBalance', 0))
        logger.info(f"Current balance: ${balance:.2f}")
        
        # Define order parameters
        symbol = 'ETHUSDT'
        min_notional = 20.0  # Binance minimum order value in USDT
        
        # Get current ETH price for info
        ticker = await client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        logger.info(f"Current ETH price: ${current_price:.2f}")
        
        # Calculate minimum quantity needed
        min_quantity = min_notional / current_price
        quantity = round(min_quantity * 1.1, 3)  # Add 10% buffer and round to 3 decimals
        order_value = current_price * quantity
        
        logger.info(f"Minimum order value: ${min_notional}")
        logger.info(f"Calculated quantity: {quantity} ETH")
        logger.info(f"Order value: ${order_value:.2f}")
        
        # Check if we have enough balance
        if balance < order_value * 0.1:  # Need at least 10% for margin
            logger.error(f"Insufficient balance. Need at least ${order_value * 0.1:.2f} for margin")
            return
        
        # Place market buy order
        logger.info(f"Placing market buy order for {quantity} ETH...")
        order = await client.futures_create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )
        
        # Log order details
        logger.info("Order placed successfully!")
        logger.info(f"Order ID: {order['orderId']}")
        logger.info(f"Status: {order['status']}")
        logger.info(f"Symbol: {order['symbol']}")
        logger.info(f"Side: {order['side']}")
        logger.info(f"Quantity: {order['origQty']}")
        
        if 'avgPrice' in order:
            logger.info(f"Average Price: ${float(order['avgPrice']):.2f}")
        
        # Get updated position
        await asyncio.sleep(1)  # Wait a moment for position to update
        positions = account_info.get('positions', [])
        eth_position = next((p for p in positions if p['symbol'] == symbol), None)
        
        if eth_position:
            position_amt = float(eth_position.get('positionAmt', 0))
            if position_amt != 0:
                logger.info(f"\nCurrent ETH position: {position_amt} ETH")
                logger.info(f"Entry price: ${float(eth_position.get('entryPrice', 0)):.2f}")
                logger.info(f"Unrealized PnL: ${float(eth_position.get('unrealizedProfit', 0)):.2f}")
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error: {e}")
        if "restricted location" in str(e):
            logger.error("⚠️  Your location is restricted. Use a VPN or Binance.US")
        elif "Invalid API" in str(e):
            logger.error("⚠️  Invalid API key or secret")
        elif "Insufficient balance" in str(e):
            logger.error("⚠️  Insufficient balance for this trade")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if client:
            await client.close_connection()
            logger.info("Connection closed")

async def main():
    """Main function"""
    logger.info("=" * 50)
    logger.info("BINANCE ETH BUY TEST")
    logger.info("=" * 50)
    
    confirm = input("\n⚠️  This will place a REAL order to buy ETH (minimum $20 value). Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        logger.info("Test cancelled by user")
        return
    
    await test_buy_eth()
    
    logger.info("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(main())
