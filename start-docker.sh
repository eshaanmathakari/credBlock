#!/bin/bash

# DeFi Credit Tracker - Docker Startup Script
# This script starts the application using Docker Compose

echo "🐳 Starting DeFi Credit Tracker with Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created. Please update the configuration as needed."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker compose down 2>/dev/null

# Start the services
echo "🚀 Starting services with Docker Compose..."
docker compose up --build

echo ""
echo "🎉 DeFi Credit Tracker is now running with Docker!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "🛑 To stop the services, press Ctrl+C"
