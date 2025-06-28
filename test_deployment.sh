#!/bin/bash

# Test script to verify the deployment workflow improvements
# This script simulates the local environment to test our PowerShell deployment script

echo "=== Testing Binance Trade Copier Deployment Script ==="
echo "This script tests the deployment logic in a Linux environment"
echo ""

# Create a test directory structure
TEST_DIR="/tmp/binance_trade_copier_test"
echo "Creating test directory: $TEST_DIR"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

# Initialize a git repository
cd "$TEST_DIR"
echo "Initializing test git repository..."
git init
echo "# Test Repository" > README.md
git add README.md
git commit -m "Initial commit"

# Create main.py for testing
echo "Creating test main.py..."
cat > main.py << 'EOF'
#!/usr/bin/env python3
import time
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            response = {
                "status": "healthy",
                "service": "Binance Trade Copier",
                "timestamp": datetime.now().isoformat(),
                "copying_active": False,
                "active_connections": 0
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == '__main__':
    print("Starting test Binance Trade Copier server on http://localhost:8000")
    server = HTTPServer(('localhost', 8000), HealthHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
EOF

chmod +x main.py

# Create a simple deployment test script (bash version of our PowerShell script)
echo "Creating test deployment script..."
cat > deploy_test.sh << 'EOF'
#!/bin/bash

PROJECT_PATH="${1:-$(pwd)}"
SKIP_GIT_PULL="${2:-false}"
SKIP_RESTART="${3:-false}"

echo "=== Test Deployment Script ==="
echo "Project Path: $PROJECT_PATH"
echo "Skip Git Pull: $SKIP_GIT_PULL"
echo "Skip Restart: $SKIP_RESTART"
echo ""

# Function to write status
write_status() {
    local message="$1"
    local status="${2:-INFO}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$status" in
        "SUCCESS") echo "[$timestamp] ✅ $message" ;;
        "ERROR") echo "[$timestamp] ❌ $message" ;;
        "WARNING") echo "[$timestamp] ⚠️ $message" ;;
        *) echo "[$timestamp] ℹ️ $message" ;;
    esac
}

# Change to project directory
write_status "Changing to project directory: $PROJECT_PATH"
if [ ! -d "$PROJECT_PATH" ]; then
    write_status "Project directory does not exist: $PROJECT_PATH" "ERROR"
    exit 1
fi

cd "$PROJECT_PATH"
write_status "Changed to directory: $(pwd)"

# Verify this is a git repository
if [ ! -d ".git" ]; then
    write_status "Not a git repository. Missing .git directory." "ERROR"
    exit 1
fi

# Git operations (unless skipped)
if [ "$SKIP_GIT_PULL" != "true" ]; then
    write_status "Git operations would be performed here (simulated)"
    write_status "Current commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
else
    write_status "Skipping git pull operations" "WARNING"
fi

# Stop existing Python processes (unless skipped)
if [ "$SKIP_RESTART" != "true" ]; then
    write_status "Stopping existing Python processes..."
    # Find and kill python processes running main.py
    pkill -f "python.*main.py" 2>/dev/null || true
    sleep 2
    
    # Start the application in background
    write_status "Starting test application..."
    python3 main.py &
    PYTHON_PID=$!
    write_status "Started application with process ID: $PYTHON_PID"
    
    # Wait for application to initialize
    sleep 3
else
    write_status "Skipping application restart" "WARNING"
fi

# Test health endpoint
write_status "Testing health endpoint..."
for i in {1..3}; do
    write_status "Health check attempt $i/3..."
    if curl -s -f http://localhost:8000/health > /dev/null; then
        write_status "Health endpoint is responding" "SUCCESS"
        RESPONSE=$(curl -s http://localhost:8000/health)
        write_status "Response: $RESPONSE"
        break
    else
        write_status "Health endpoint check failed" "WARNING"
        if [ $i -lt 3 ]; then
            write_status "Retrying in 2 seconds..."
            sleep 2
        fi
    fi
done

# Final verification
if curl -s -f http://localhost:8000/health > /dev/null; then
    write_status "=== Deployment test completed successfully ===" "SUCCESS"
    
    # Cleanup
    write_status "Cleaning up test processes..."
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null || true
    fi
    pkill -f "python.*main.py" 2>/dev/null || true
    
    exit 0
else
    write_status "=== Deployment test failed ===" "ERROR"
    
    # Cleanup
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null || true
    fi
    pkill -f "python.*main.py" 2>/dev/null || true
    
    exit 1
fi
EOF

chmod +x deploy_test.sh

echo "Running deployment test..."
echo ""
./deploy_test.sh "$TEST_DIR"
TEST_RESULT=$?

echo ""
echo "=== Test Results ==="
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ Deployment test PASSED"
    echo "The deployment logic appears to be working correctly."
else
    echo "❌ Deployment test FAILED"
    echo "There may be issues with the deployment logic."
fi

echo ""
echo "Cleaning up test directory..."
rm -rf "$TEST_DIR"

echo "=== Test Complete ==="
exit $TEST_RESULT