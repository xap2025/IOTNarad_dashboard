#!/bin/bash
# Fix Port 1883 Already in Use Error

echo "🔍 Checking what's using port 1883..."

# Method 1: Check with lsof
if command -v lsof &> /dev/null; then
    echo "Using lsof:"
    sudo lsof -i :1883
fi

# Method 2: Check with netstat
if command -v netstat &> /dev/null; then
    echo "Using netstat:"
    sudo netstat -tulpn | grep 1883
fi

# Method 3: Check with ss
if command -v ss &> /dev/null; then
    echo "Using ss:"
    sudo ss -ltnp | grep 1883
fi

# Method 4: Check Docker containers
echo "Checking Docker containers:"
docker ps -a | grep mqtt
docker ps -a | grep 1883

echo ""
echo "✅ If you see any process above, we'll stop it next..."

