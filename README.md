# DeFi Credit Tracker - Production Edition

A comprehensive DeFi credit scoring platform with multichain support, real-time staking/governance data, and ML-powered risk assessment.

## Features

### 🚀 Production-Ready Features
- **Real SEI Staking/Governance Integration**: Live data from SEI precompile contracts
- **Multichain Support**: SEI, Ethereum, and Solana with unified API
- **ML-Powered Scoring**: Advanced feature engineering and model training pipeline
- **Production API**: FastAPI with rate limiting, caching, and health checks
- **Mobile-Ready**: RESTful API with consistent response schemas

### 🔧 Technical Stack
- **Backend**: FastAPI, Redis, PostgreSQL, Web3
- **ML Pipeline**: Scikit-learn, XGBoost, LightGBM with S3 model storage
- **Frontend**: React, TypeScript, Tailwind CSS
- **Chrome Extension**: Real-time credit scores on blockchain explorers

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Redis
- PostgreSQL (optional for production)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the production server
python production_server.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Chrome Extension

```bash
cd chrome-extension

# Load extension in Chrome
# 1. Go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked" and select the chrome-extension folder
```

## Environment Variables

### Required Variables
```bash
# SEI Configuration
SEI_RPC_URL=https://evm-rpc.sei-apis.com
SEI_STAKING_CONTRACT=0x...
SEI_GOVERNANCE_CONTRACT=0x...

# Ethereum Configuration
ETHEREUM_RPC=https://mainnet.infura.io/v3/YOUR_KEY
ETHERSCAN_API_KEY=your_etherscan_key

# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Database
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://user:pass@localhost:5432/defi_tracker

# ML Model Storage
MODEL_S3_BUCKET=your-model-bucket
MODEL_S3_KEY=models/credit_scorer.joblib

# API Configuration
RATE_LIMIT_PER_MINUTE=60
CACHE_TTL_SECONDS=300
```

### Optional Variables
```bash
# Price Data APIs
CMC_API_KEY=your_coinmarketcap_key
BINANCE_API_KEY=your_binance_key

# Additional RPC URLs
POLYGON_RPC=https://polygon-mainnet.infura.io/v3/YOUR_KEY
ARBITRUM_RPC=https://arbitrum-mainnet.infura.io/v3/YOUR_KEY
```

## API Documentation

### Credit Score Endpoint
```http
GET /v1/score/{wallet}?chain={sei|eth|sol}
```

**Response:**
```json
{
  "wallet": "0x...",
  "chain": "sei",
  "score": 750,
  "risk": "Low Risk",
  "confidence": 0.85,
  "factors": {
    "Account Age": 25,
    "Tx Activity": 40,
    "Balances": 30,
    "DeFi Extras": 35,
    "Staking": 20,
    "Governance": 15
  },
  "latency_ms": 150,
  "model_version": "v1.0.0",
  "last_updated": 1703123456
}
```

### Health Check
```http
GET /health
```

## ML Pipeline

### Training Models
```bash
cd backend/ml

# Train with synthetic data
python train.py --samples 10000 --version v1.0.0

# Train with custom S3 bucket
python train.py --s3-bucket your-bucket --s3-key models/credit_scorer.joblib
```

### Feature Engineering
The system extracts 20+ features including:
- Transaction patterns (velocity, burstiness, periodicity)
- Portfolio diversity (Herfindahl index, blue-chip ratio)
- Protocol interactions (lending, DEX, bridges)
- Behavioral risk (mixer usage, sanctioned entity proximity)
- Staking and governance participation

## Architecture

### Backend Services
```
backend/
├── services/
│   ├── sei_staking.py      # SEI staking precompile integration
│   └── sei_governance.py   # SEI governance precompile integration
├── chains/
│   ├── base.py            # Chain adapter interface
│   ├── sei.py             # SEI implementation
│   ├── eth.py             # Ethereum implementation
│   └── sol.py             # Solana implementation
├── ml/
│   ├── features.py        # Feature engineering
│   ├── train.py           # Model training
│   └── serve.py           # Model serving
└── production_server.py   # Main FastAPI application
```

### Frontend Components
```
frontend/src/
├── components/
│   ├── CreditScoreDisplay.tsx
│   ├── WalletInput.tsx
│   └── ui/                 # Shadcn/ui components
├── pages/
│   └── Index.tsx          # Main page with chain selector
└── App.tsx
```

## Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run specific test files
pytest tests/test_sei_staking.py
pytest tests/test_sei_governance.py

# Run with coverage
pytest --cov=services --cov=chains --cov=ml
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual services
docker build -t defi-credit-backend ./backend
docker build -t defi-credit-frontend ./frontend
```

### Production Checklist
- [ ] Set up Redis cluster for caching
- [ ] Configure PostgreSQL for persistent storage
- [ ] Set up S3 bucket for model storage
- [ ] Configure CDN for frontend assets
- [ ] Set up monitoring and logging
- [ ] Configure SSL certificates
- [ ] Set up CI/CD pipeline

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Join our Discord community
- Email: support@defi-credit-tracker.com

## Roadmap

### Phase 2 (Q2 2024)
- [ ] Real-time price feeds
- [ ] Advanced ML models (deep learning)
- [ ] More blockchain support (Polygon, Arbitrum)
- [ ] Mobile app development

### Phase 3 (Q3 2024)
- [ ] DeFi protocol integrations
- [ ] Social credit scoring
- [ ] API marketplace
- [ ] Enterprise features

---

**Built with ❤️ for the DeFi community**
