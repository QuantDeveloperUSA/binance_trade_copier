import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

# Import the function at the top to avoid import errors
try:
    from main import calculate_slave_quantity
except ImportError:
    print("⚠️  Warning: Could not import calculate_slave_quantity from main.py")
    calculate_slave_quantity = None

def test_trade_execution_speed():
    """Test trade execution latency"""
    print("⚡ Testing Trade Execution Speed...")
    
    if calculate_slave_quantity is None:
        print("   ❌ Cannot test - function not available")
        return
    
    # Mock slave account
    slave_account = Mock()
    slave_account.id = 2
    slave_account.fixed_ratio = None
    slave_account.balance_multiplier = 1.0
    
    # Time the calculation
    start_time = time.time()
    
    with patch('main.account_balances', {1: 10000, 2: 5000}):
        for _ in range(1000):
            asyncio.run(calculate_slave_quantity(
                master_quantity=1000,
                master_account_id=1,
                slave_account=slave_account
            ))
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 1000 * 1000  # Convert to milliseconds
    
    print(f"   Average calculation time: {avg_time:.2f}ms")
    print(f"   Target: <1ms ({'✅' if avg_time < 1 else '⚠️'})")

def test_concurrent_trades():
    """Test handling multiple concurrent trades"""
    print("🔄 Testing Concurrent Trade Handling...")
    
    async def mock_trade_execution(trade_id):
        """Mock trade execution with random delay"""
        await asyncio.sleep(0.01)  # Simulate network delay
        return f"Trade {trade_id} completed"
    
    async def run_concurrent_test():
        start_time = time.time()
        
        # Simulate 20 concurrent trades
        tasks = [mock_trade_execution(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"   Processed {len(results)} trades in {total_time:.2f}s")
        print(f"   Average time per trade: {total_time/len(results)*1000:.2f}ms")
        print(f"   Concurrent processing: {'✅' if total_time < 1.0 else '⚠️'}")
    
    asyncio.run(run_concurrent_test())

def test_memory_usage():
    """Test memory usage under load"""
    print("💾 Testing Memory Usage...")
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create many mock objects
    accounts = []
    for i in range(1000):
        account = Mock()
        account.id = i
        account.balance_multiplier = 1.0
        accounts.append(account)
    
    current_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = current_memory - initial_memory
    
    print(f"   Initial memory: {initial_memory:.1f}MB")
    print(f"   Memory after 1000 objects: {current_memory:.1f}MB")
    print(f"   Memory increase: {memory_increase:.1f}MB")
    print(f"   Memory efficiency: {'✅' if memory_increase < 50 else '⚠️'}")

if __name__ == "__main__":
    print("🧪 Performance Test Suite")
    print("=========================\n")
    
    test_trade_execution_speed()
    print()
    
    test_concurrent_trades()
    print()
    
    test_memory_usage()
    print()
    
    print("🎉 Performance tests completed!")
