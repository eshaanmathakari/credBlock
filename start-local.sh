#!/bin/bash

# DeFi Credit Tracker - Local Development Startup Script
# This script helps you run the application locally with proper configuration

echo "🚀 Starting DeFi Credit Tracker locally..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created. Please update the configuration as needed."
fi

# Check if Redis is running
echo "🔍 Checking Redis..."
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is not running. Starting Redis with Docker..."
    if command -v docker &> /dev/null; then
        # Check if Redis container is already running
        if docker ps | grep -q "redis:7-alpine"; then
            echo "✅ Redis container is already running"
        else
            echo "🐳 Starting Redis container..."
            docker run -d --name redis-local -p 6379:6379 redis:7-alpine
            echo "✅ Redis started on port 6379"
        fi
    else
        echo "❌ Docker not found. Please install Docker or Redis:"
        echo "   brew install redis  # macOS"
        echo "   sudo apt-get install redis-server  # Ubuntu"
        exit 1
    fi
else
    echo "✅ Redis is already running"
fi

# Check if PostgreSQL is running (optional)
echo "🔍 Checking PostgreSQL..."
if ! pgrep -x "postgres" > /dev/null; then
    echo "⚠️  PostgreSQL is not running. Starting PostgreSQL with Docker..."
    if command -v docker &> /dev/null; then
        # Check if PostgreSQL container is already running
        if docker ps | grep -q "postgres:15-alpine"; then
            echo "✅ PostgreSQL container is already running"
        else
            echo "🐳 Starting PostgreSQL container..."
            docker run -d --name postgres-local -p 5432:5432 -e POSTGRES_DB=defi_tracker -e POSTGRES_USER=defi_user -e POSTGRES_PASSWORD=defi_password postgres:15-alpine
            echo "✅ PostgreSQL started on port 5432"
        fi
    else
        echo "⚠️  PostgreSQL is optional for basic functionality."
    fi
else
    echo "✅ PostgreSQL is running"
fi

# Start backend
echo "🔧 Starting backend server..."
cd backend

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
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

echo "🌐 Starting backend on http://localhost:8001"
echo "   Health check: http://localhost:8001/health"
echo "   API docs: http://localhost:8001/docs"

# Start backend in background
python3 production_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Test backend health
echo "🔍 Testing backend health..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend..."
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "🌐 Starting frontend on http://localhost:8080"
echo "   Frontend will connect to backend at http://localhost:8001"

# Set environment variable for frontend
export VITE_API_BASE_URL=http://localhost:8001

# Start frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 DeFi Credit Tracker is now running!"
echo ""
echo "📱 Frontend: http://localhost:8080"
echo "🔧 Backend:  http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "🛑 To stop the servers, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    
    # Optionally stop Docker containers (commented out to keep them running)
    # echo "🐳 Stopping Docker containers..."
    # docker stop redis-local postgres-local 2>/dev/null
    # docker rm redis-local postgres-local 2>/dev/null
    
    echo "✅ Servers stopped"
    echo "💡 Docker containers (Redis/PostgreSQL) are still running for future use"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
