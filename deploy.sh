#!/bin/bash

# DeFi Credit Tracker Deployment Script
set -e

echo "🚀 DeFi Credit Tracker Deployment Script"
echo "========================================"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ ! -f .env.example ]; then
        echo "❌ Missing .env.example template. Please add it before deploying."
        exit 1
    fi
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   Required variables:"
    echo "   - ETHEREUM_RPC (Infura/Alchemy URL)"
    echo "   - ETHERSCAN_API_KEY (for Ethereum lookups)"
    echo "   - SOLANA_RPC_URL (Helius/Alchemy/Ankr URL)"
    echo "   - VITE_API_BASE_URL (frontend API base, defaults to http://localhost:8001)"
    echo "   - MODEL_S3_BUCKET / AWS_* (only if loading models from S3)"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("ETHEREUM_RPC" "SOLANA_RPC_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set in .env file"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check backend health
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API health check failed"
    docker-compose logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend health check failed"
    docker-compose logs frontend
    exit 1
fi

# Check Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis health check failed"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Services:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8001"
echo "   - API Docs: http://localhost:8001/docs"
echo "   - Redis: localhost:6379"
echo "   - PostgreSQL: localhost:5432"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo "   - Train ML model: docker-compose --profile training run ml-trainer"
echo ""
echo "📝 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Test the credit scoring with a wallet address"
echo "   3. Check the API documentation at http://localhost:8001/docs"
echo "   4. Monitor logs with: docker-compose logs -f"
