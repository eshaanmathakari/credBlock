# CredBlock - DeFi Credit Tracker

📌 **Overview**

DeFi Credit Tracker (CredBlock) is a decentralized credit scoring and risk analysis platform built to bring transparency, accessibility, and fairness to Web3 financial ecosystems.

Instead of relying on opaque, centralized credit bureaus, CredBlock leverages on-chain activity, multi-chain wallet analytics, and machine learning models to generate a dynamic creditworthiness profile for users across SEI, Ethereum, and Solana networks.

## 🚀 Key Features

### 🔗 Multi-Chain Support
Integrated with SEI, Ethereum, and Solana RPC endpoints to track wallet activity, staking, governance, and transaction histories.

### 🤖 AI-Powered Credit Scoring
ML models (hosted on AWS & auto-updated via S3) generate risk-adjusted credit scores using wallet behavior, portfolio diversity, and transaction frequency.

### 📊 Real-Time Risk Analytics
Monitors on-chain activity with Redis caching and PostgreSQL persistence to deliver fast, low-latency queries.

### ⚡ API & Dashboard
REST APIs with CORS/host filtering and a frontend dashboard to visualize scores, history, and DeFi credit profiles.

### 🛡️ Security & Transparency
Built with clear environment-based configuration, API rate limits, and Prometheus metrics for monitoring.

## 🛠️ Tech Stack

**Backend:** Python (FastAPI), Node.js, Redis, PostgreSQL

**Frontend:** React + Vite + TailwindCSS

**Blockchain Integrations:**
- SEI Precompiles (Staking & Governance)
- Ethereum RPC & Etherscan APIs
- Solana RPC & WebSocket APIs

**Infrastructure:**
- Docker & Docker Compose (multi-arch: ARM64 & AMD64)
- AWS EC2 (Amazon Linux 2023)
- AWS ECR (container registry), S3 (ML models), CloudWatch/Grafana

**Machine Learning:** Joblib models for credit scoring, cached with TTL for fast inference

## 🌐 Architecture

**Data Layer** – Collects wallet data from SEI, Ethereum, Solana.

**Processing Layer** – ML models analyze wallet activity and generate credit scores.

**API Layer** – Exposes credit scoring APIs and monitoring endpoints.

**Frontend Dashboard** – Displays credit scores and wallet health in a user-friendly way.

## 💡 Why This Matters

Traditional credit systems exclude millions. DeFi and Web3 offer inclusion, but lack trusted creditworthiness tools.

CredBlock bridges this gap by:
- Building trustless, transparent scoring
- Encouraging responsible borrowing/lending in DeFi
- Enabling new forms of on-chain credit markets

## 🏆 Hackathon Contribution

- Multi-chain integration (SEI, Ethereum, Solana)
- Containerized multi-arch deployment for portability
- AI-driven credit scoring pipeline
- API + dashboard ready for real DeFi apps to consume

## 🔮 Future Roadmap

- Expand to more chains (Polygon, BNB, Avalanche)
- Integrate zkML for privacy-preserving credit scoring
- Launch a mobile-first version for DeFi users globally
- Build partnerships with DeFi lenders & wallets for adoption

---

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

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
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

---

**✦ CredBlock = AI x DeFi x Web3 Transparency ✦**

**Built with ❤️ for the DeFi community**
