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
        
        # Check position mode
        position_mode = await client.futures_get_position_mode()
        dual_side_position = position_mode.get('dualSidePosition', False)
        logger.info(f"Position mode: {'Hedge Mode' if dual_side_position else 'One-way Mode'}")
        
        # Define order parameters
        symbol = 'ETHUSDT'
        min_notional = 20.0  # Binance minimum order value in USDT
        
        # Get current ETH price for info
        ticker = await client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        logger.info(f"Current ETH price: ${current_price:.2f}")
        
        # Ask user for order size
        print(f"\nMinimum order value: ${min_notional}")
        order_value_input = input(f"Enter order value in USDT (minimum ${min_notional}): $")
        
        try:
            order_value = float(order_value_input)
            if order_value < min_notional:
                logger.error(f"Order value must be at least ${min_notional}")
                return
        except ValueError:
            logger.error("Invalid order value entered")
            return
        
        # Calculate quantity
        quantity = round(order_value / current_price, 3)
        actual_value = current_price * quantity
        
        logger.info(f"Order quantity: {quantity} ETH")
        logger.info(f"Actual order value: ${actual_value:.2f}")
        
        # Check if we have enough balance
        if balance < actual_value * 0.1:  # Need at least 10% for margin
            logger.error(f"Insufficient balance. Need at least ${actual_value * 0.1:.2f} for margin")
            return
        
        # Place market buy order
        logger.info(f"Placing market buy order for {quantity} ETH...")
        
        # Prepare order parameters
        order_params = {
            'symbol': symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': quantity
        }
        
        # Add position side if in hedge mode
        if dual_side_position:
            order_params['positionSide'] = 'LONG'
        
        order = await client.futures_create_order(**order_params)
        
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
        # Fetch fresh account info for updated positions
        account_info = await client.futures_account()
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
        elif "position side does not match" in str(e):
            logger.error("⚠️  Position mode mismatch. Check your account's position mode settings")
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
    logger.info("BINANCE FUTURES ETH BUY TEST")
    logger.info("=" * 50)
    
    confirm = input("\n⚠️  This will place a REAL futures order to buy ETH. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        logger.info("Test cancelled by user")
        return
    
    await test_buy_eth()
    
    logger.info("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(main())
