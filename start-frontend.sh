#!/bin/bash

# Frontend Startup Script for DeFi Credit Tracker
# This script starts only the frontend server

echo "🎨 Starting DeFi Credit Tracker Frontend..."

# Change to frontend directory
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Set environment variable for frontend
export VITE_API_BASE_URL=http://localhost:8001

# Start the frontend server
echo "🌐 Starting frontend server on http://localhost:8080"
echo "   Frontend will connect to backend at http://localhost:8001"
echo ""
echo "🛑 Press Ctrl+C to stop the server"

# Start the server
npm run dev
