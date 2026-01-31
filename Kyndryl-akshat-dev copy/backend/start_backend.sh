#!/bin/bash

# Kill any process using port 8000
echo "Checking for processes on port 8000..."
PID=$(lsof -ti:8000)
if [ ! -z "$PID" ]; then
    echo "Killing process $PID on port 8000..."
    kill -9 $PID
    sleep 0.5
fi

# Navigate to src directory and start backend
cd "$(dirname "$0")/src"
echo "Starting backend on port 8000..."
python3 main.py
