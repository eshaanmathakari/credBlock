#!/bin/bash

# AWS ECR deployment script for CredBlock
echo "🚀 CredBlock AWS ECR Deployment"
echo "================================"

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found. Please create it first."
    exit 1
fi

# Check required environment variables
if [ -z "$CMC_API_KEY" ]; then
    echo "❌ CMC_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$EC2_INSTANCE_ID" ]; then
    echo "❌ EC2_INSTANCE_ID not set in .env file"
    exit 1
fi

# AWS ECR Repository details
ECR_REGISTRY="983240697534.dkr.ecr.us-east-1.amazonaws.com"
ECR_REPOSITORY="credblock"
ECR_REGION="us-east-1"

echo "✅ Environment variables loaded"
echo "🔑 CMC API Key: ${CMC_API_KEY:0:8}..."
echo "🖥️  EC2 Instance: $EC2_INSTANCE_ID"
echo "📦 ECR Registry: $ECR_REGISTRY"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install AWS CLI first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ AWS CLI and Docker found"

# Authenticate to ECR
echo "🔐 Authenticating to ECR..."
aws ecr get-login-password --region $ECR_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

if [ $? -ne 0 ]; then
    echo "❌ ECR authentication failed. Check your AWS credentials."
    exit 1
fi

echo "✅ ECR authentication successful"

# Build Docker image
echo "🔨 Building CredBlock Docker image..."
docker build -t credblock .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed."
    exit 1
fi

echo "✅ Docker image built successfully"

# Tag the image for ECR
echo "🏷️  Tagging image for ECR..."
docker tag credblock:latest $ECR_REGISTRY/$ECR_REPOSITORY:latest

# Push to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

if [ $? -ne 0 ]; then
    echo "❌ Failed to push image to ECR."
    exit 1
fi

echo "✅ Image pushed to ECR successfully"

# Create docker-compose file for EC2
echo "📝 Creating docker-compose file for EC2..."
cat > docker-compose.ec2.yml << EOF
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  credblock:
    image: $ECR_REGISTRY/$ECR_REPOSITORY:latest
    ports:
      - "80:80"
    environment:
      - REDIS_URL=redis://redis:6379
      - SEI_RPC_URL=https://evm-rpc.sei-apis.com
      - ETHEREUM_RPC=$ETHEREUM_RPC
      - SOLANA_RPC_URL=$SOLANA_RPC_URL
      - CMC_API_KEY=$CMC_API_KEY
      - ETHERSCAN_API_KEY=$ETHERSCAN_API_KEY
      - MODEL_S3_BUCKET=$MODEL_S3_BUCKET
      - MODEL_S3_KEY=$MODEL_S3_KEY
      - AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
      - AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
      - RATE_LIMIT_PER_MINUTE=60
      - CACHE_TTL_SECONDS=300
      - LOG_LEVEL=INFO
      - DEBUG=false
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
EOF

echo "✅ Docker Compose file created for EC2"

# Copy files to EC2 (if you have SSH access)
echo "📤 Copying deployment files to EC2..."
if command -v scp &> /dev/null; then
    # You'll need to set up SSH key or use AWS Systems Manager
    echo "⚠️  Manual step required: Copy docker-compose.ec2.yml to your EC2 instance"
    echo "   You can use: scp docker-compose.ec2.yml ec2-user@your-ec2-ip:~/"
else
    echo "⚠️  SCP not available. Please manually copy docker-compose.ec2.yml to your EC2 instance"
fi

echo ""
echo "🎉 ECR Deployment Complete!"
echo "================================"
echo "📦 Image: $ECR_REGISTRY/$ECR_REPOSITORY:latest"
echo "🖥️  EC2 Instance: $EC2_INSTANCE_ID"
echo ""
echo "📋 Next steps on your EC2 instance:"
echo "   1. Copy docker-compose.ec2.yml to EC2"
echo "   2. Install Docker and Docker Compose on EC2"
echo "   3. Run: docker-compose -f docker-compose.ec2.yml up -d"
echo "   4. Access your app at: http://your-ec2-public-ip"
echo ""
echo "🔧 EC2 Setup Commands:"
echo "   # Install Docker"
echo "   sudo yum update -y"
echo "   sudo yum install -y docker"
echo "   sudo service docker start"
echo "   sudo usermod -a -G docker ec2-user"
echo ""
echo "   # Install Docker Compose"
echo "   sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose"
echo "   sudo chmod +x /usr/local/bin/docker-compose"
echo ""
echo "   # Deploy the app"
echo "   docker-compose -f docker-compose.ec2.yml up -d"
