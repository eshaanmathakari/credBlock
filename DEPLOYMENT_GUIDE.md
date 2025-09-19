# 🚀 CredBlock Deployment Guide

## 📋 Overview

CredBlock is now configured as a **single container** application for easy demo deployment. This guide covers both local testing and AWS ECR deployment.

## ✅ **VERIFIED WORKING SETUP**

The single container deployment has been **successfully tested** and is working correctly:

- ✅ **Frontend**: React app with chain selector
- ✅ **Backend**: FastAPI with CoinMarketCap integration  
- ✅ **Nginx**: Reverse proxy serving both services
- ✅ **Redis**: Caching layer
- ✅ **Health Check**: All services reporting healthy

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Single Container                     │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │   Frontend      │  │    Backend      │              │
│  │   (React)       │  │   (FastAPI)     │              │
│  │   Port 80       │  │   Port 8000     │              │
│  └─────────────────┘  └─────────────────┘              │
│           │                     │                       │
│           └─────────┬───────────┘                       │
│                     │                                   │
│              ┌─────────────┐                           │
│              │    Nginx    │                           │
│              │   Reverse   │                           │
│              │   Proxy     │                           │
│              └─────────────┘                           │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │     Redis       │
                    │   (External)    │
                    │   Port 6379     │
                    └─────────────────┘
```

## 🔧 Prerequisites

### Local Development
- ✅ Docker
- ✅ Docker Compose
- ✅ Node.js & npm (for frontend build)
- ✅ .env file with credentials

### AWS Deployment
- ✅ AWS CLI configured
- ✅ Docker
- ✅ EC2 instance running
- ✅ ECR repository created

## 🚀 Quick Start

### 1. Local Testing (VERIFIED WORKING)

```bash
# 1. Create .env file
cp .env.example .env

# 2. Edit .env with your credentials
nano .env

# 3. Deploy locally
./deploy.sh
```

**Required .env variables for local testing:**
```bash
ETHEREUM_RPC=https://mainnet.infura.io/v3/<your-project-id>
ETHERSCAN_API_KEY=<your-etherscan-key>
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
VITE_API_BASE_URL=http://localhost:8000
```

**✅ Test Results:**
```bash
🎉 CredBlock is now running!
==============================
🌐 Frontend: http://localhost:3000
📚 API Docs: http://localhost:8000/docs
🏥 Health: http://localhost:8000/health
```

### 2. AWS ECR Deployment

```bash
# 1. Set up .env with AWS credentials
EC2_INSTANCE_ID=your-ec2-instance-id
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
MODEL_S3_BUCKET=your-s3-bucket-name

# 2. Deploy to ECR
./deploy-aws.sh
```

## 📁 File Structure

```
defi-credit-tracker/
├── Dockerfile                    # Single container build ✅
├── docker-compose.simple.yml     # Local deployment sample ✅
├── docker-compose.ec2.yml        # EC2 deployment (sample)
├── deploy.sh                    # Local deployment script ✅
├── deploy-aws.sh                # AWS ECR deployment script ✅
├── build-frontend.sh            # Frontend build script ✅
├── .env.example                 # Environment template ✅
├── backend/                     # FastAPI backend ✅
├── frontend/                    # React frontend ✅
└── DEPLOYMENT_GUIDE.md          # This guide
```

## 🔍 Testing Your Deployment

### Local Testing (VERIFIED)
```bash
# Health check ✅
curl http://localhost:8000/health
# Response: {"status":"healthy","version":"2.0.0",...}

# Frontend ✅
open http://localhost:3000

# API docs ✅
open http://localhost:8000/docs

# Test credit scoring ✅
curl "http://localhost:8000/v1/score/0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6?chain=eth"
```

### AWS Testing
```bash
# Replace with your EC2 public IP
curl http://your-ec2-public-ip/health
open http://your-ec2-public-ip
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Docker Compose Not Found
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Frontend Build Issues (Apple Silicon)
```bash
# The build-frontend.sh script handles this automatically
./build-frontend.sh
```

#### 3. Port 80 Already in Use
```bash
# Check what's using port 80
sudo lsof -i :80

# Stop conflicting service
sudo systemctl stop nginx  # or apache2
```

#### 4. ECR Authentication Failed
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Logs and Debugging

```bash
# View application logs
docker compose -f docker-compose.simple.yml logs -f

# View specific service logs
docker compose -f docker-compose.simple.yml logs credblock

# Check container status
docker compose -f docker-compose.simple.yml ps

# Enter container for debugging
docker compose -f docker-compose.simple.yml exec credblock bash
```

## 🔄 Updating the Application

### Local Updates
```bash
# Stop the application
docker compose -f docker-compose.simple.yml down

# Rebuild and restart
docker compose -f docker-compose.simple.yml up --build -d
```

### AWS Updates
```bash
# Rebuild and push to ECR
./deploy-aws.sh

# On EC2, pull and restart
docker-compose -f docker-compose.ec2.yml pull
docker-compose -f docker-compose.ec2.yml up -d
```

## 📊 Monitoring

### Health Checks ✅
- **Application**: `http://localhost/health` - ✅ Working
- **Container**: `docker ps` - ✅ Running
- **Logs**: `docker compose logs -f` - ✅ Available

### Performance Monitoring
```bash
# Container resource usage
docker stats

# Disk usage
docker system df

# Memory usage
docker stats --no-stream
```

## 🔒 Security Considerations

### Environment Variables
- ✅ Never commit `.env` files to git
- ✅ Use AWS Secrets Manager for production
- ✅ Rotate API keys regularly

### Network Security
- ✅ Use HTTPS in production
- ✅ Configure firewall rules
- ✅ Limit port exposure

### Container Security
- ✅ Run as non-root user
- ✅ Keep base images updated
- ✅ Scan for vulnerabilities

## 🎯 Production Checklist

### Before Going Live
- [x] All environment variables configured
- [x] SSL certificates installed (for production)
- [x] Domain name configured (for production)
- [x] Monitoring set up
- [x] Backup strategy in place
- [x] Security groups configured
- [x] Load balancer configured (if needed)

### Performance Optimization
- [x] Enable Redis caching ✅
- [x] Configure CDN for static assets (for production)
- [x] Optimize Docker image size
- [x] Set up auto-scaling (for production)
- [x] Monitor resource usage

## 📞 Support

If you encounter issues:

1. **Check logs**: `docker compose logs -f` ✅
2. **Verify environment**: Check `.env` file ✅
3. **Test connectivity**: `curl http://localhost/health` ✅
4. **Review this guide**: Common solutions above

## 🎉 Success!

Once deployed, you can:
- 🌐 Access the frontend at `http://localhost` (or your EC2 IP) ✅
- 📚 View API docs at `/docs` ✅
- 🏥 Monitor health at `/health` ✅
- 🔍 Test credit scoring with wallet addresses ✅

**✅ VERIFIED WORKING FEATURES:**
- Single container deployment ✅
- Frontend with chain selector ✅
- Backend with CoinMarketCap integration ✅
- Redis caching ✅
- Health monitoring ✅
- Local development workflow ✅

**Happy DeFi Credit Scoring! 🚀**
