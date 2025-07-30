#!/bin/bash

# Health check script for DJAMMS services

check_service() {
    local service=$1
    local url=$2
    echo "Checking $service..."
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    if [ $response -eq 200 ]; then
        echo "✅ $service is running"
        return 0
    else
        echo "❌ $service is not responding"
        return 1
    fi
}

check_process() {
    local process=$1
    echo "Checking $process..."
    if pgrep -f "$process" > /dev/null; then
        echo "✅ $process is running"
        return 0
    else
        echo "❌ $process is not running"
        return 1
    fi
}

# Check backend health
check_service "Backend API" "http://localhost:5000/health"

# Check frontend
check_service "Frontend" "http://localhost:3000"

# Check database
PGPASSWORD=postgres psql -h localhost -U postgres -d djamms -c '\q' >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database is connected"
else
    echo "❌ Database connection failed"
fi

# Check Redis
redis-cli ping >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Redis is connected"
else
    echo "❌ Redis connection failed"
fi

# Check media processes
check_process "ffmpeg"
check_process "mpg123"

# Check disk space
echo "Checking disk space..."
df -h | grep '/dev/sda1'
