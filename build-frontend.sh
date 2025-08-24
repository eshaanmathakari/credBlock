#!/bin/bash

# Build frontend locally before Docker build
echo "🔨 Building frontend locally..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm found"

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing frontend dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

# Build the application
echo "🔨 Building frontend application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Failed to build frontend application"
    exit 1
fi

echo "✅ Frontend built successfully!"
echo "📁 Build output: frontend/dist/"

# Go back to root directory
cd ..

echo "🚀 Frontend is ready for Docker build!"
