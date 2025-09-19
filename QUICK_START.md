# 🚀 Quick Start Guide

Get the DeFi Credit Tracker up and running in minutes!

## Prerequisites

- Docker and Docker Compose installed
- Git
- Basic knowledge of blockchain addresses

## 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd defi-credit-tracker

# Copy environment template
cp .env.example .env
```

## 2. Configure Environment

Edit the `.env` file with your configuration:

```bash
# Required: Ethereum RPC endpoint
ETHEREUM_RPC=https://mainnet.infura.io/v3/<your-project-id>
ETHERSCAN_API_KEY=<your-etherscan-key>

# Required: Solana RPC endpoint  
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Optional: For ML model storage
MODEL_S3_BUCKET=<your-ml-models-bucket>
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>

# Frontend configuration
VITE_API_BASE_URL=http://localhost:8000
```

## 3. Deploy

```bash
# Run the deployment script
./deploy.sh
```

The script will:
- ✅ Validate your configuration
- 🔨 Build and start all services
- 🏥 Check service health
- 📊 Display access URLs

## 4. Test the Application

1. **Frontend**: Open http://localhost:3000
2. **API Docs**: Open http://localhost:8000/docs
3. **Test with a wallet address**:
   - SEI: `0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`
   - Ethereum: `0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`
   - Solana: `9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM`

## 5. API Usage

### Get Credit Score
```bash
curl "http://localhost:8000/v1/score/0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6?chain=sei"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

## 6. Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Train ML model
docker-compose --profile training run ml-trainer

# Update services
docker-compose up -d --build
```

## 7. Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Check environment variables
docker-compose config
```

### API not responding
```bash
# Check backend health
curl http://localhost:8000/health

# Check Redis connection
docker-compose exec redis redis-cli ping
```

### Frontend not loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

## 8. Development

### Local Development
```bash
# Backend (Python)
cd backend
pip install -r requirements.txt
uvicorn production_server:app --reload

# Frontend (Node.js)
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 9. Production Deployment

For production deployment:

1. **Update environment variables** for production endpoints
2. **Set up SSL certificates** for HTTPS
3. **Configure monitoring** (Prometheus, Grafana)
4. **Set up CI/CD** pipeline
5. **Configure backups** for Redis and PostgreSQL

## 10. Next Steps

- 🔧 Configure real SEI staking/governance contract addresses
- 🤖 Train ML models with real data
- 🔗 Implement full Ethereum and Solana integrations
- 📱 Update Chrome extension
- 📊 Add monitoring and alerting

## Support

- 📖 Full documentation: See `README.md`
- 🐛 Issues: Create a GitHub issue
- 💬 Questions: Check the documentation or create a discussion

---

**Happy DeFi Credit Scoring! 🎉**
