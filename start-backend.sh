#!/bin/bash

# Backend Startup Script for DeFi Credit Tracker
# This script starts only the backend server

echo "🔧 Starting DeFi Credit Tracker Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created. Please update the configuration as needed."
fi

# Change to backend directory
cd backend

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Install dependencies
echo "📦 Installing Python dependencies..."
# Try minimal requirements first (without lightgbm/xgboost which need CMake)
if [ -f requirements-minimal.txt ]; then
    echo "   Using minimal requirements (lightgbm/xgboost excluded)..."
    pip install -r requirements-minimal.txt --quiet
else
    pip install -r requirements.txt --quiet
fi

# Start the backend server
echo "🌐 Starting backend server on http://localhost:8001"
echo "   Health check: http://localhost:8001/health"
echo "   API docs: http://localhost:8001/docs"
echo ""
echo "🛑 Press Ctrl+C to stop the server"

# Start the server
python3 production_server.py
