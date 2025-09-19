"""
Production FastAPI Server for DeFi Credit Tracker
Integrates SEI staking/governance services, ML features, and multichain support
"""

import os
import json
import time
import asyncio
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator, ValidationError
import uvicorn
import redis.asyncio as redis
from web3 import Web3
import logging

# Import our services
from services.sei_staking import SEIStakingService, StakingMetrics
from services.sei_governance import SEIGovernanceService, GovernanceMetrics
from credit_scorer import DeFiCreditScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class CreditScoreRequest(BaseModel):
    wallet: str
    chain: str = "sei"
    
    @validator('wallet')
    def validate_wallet(cls, v):
        if not v:
            raise ValueError('Wallet address cannot be empty')
        return v.lower()
    
    @validator('chain')
    def validate_chain(cls, v):
        valid_chains = ['sei', 'eth', 'sol']
        if v not in valid_chains:
            raise ValueError(f'Chain must be one of: {valid_chains}')
        return v

class CreditScoreResponse(BaseModel):
    wallet: str
    chain: str
    score: int
    risk: str
    confidence: float
    factors: Dict[str, Any]
    latency_ms: int
    model_version: Optional[str] = None
    last_updated: int

class HealthResponse(BaseModel):
    status: str
    timestamp: int
    version: str
    services: Dict[str, str]
    model_version: Optional[str] = None
    last_loaded_at: Optional[int] = None
    price_sources_ok: bool

# Configuration
@dataclass
class Config:
    # Database URLs
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/defi_proxy")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # SEI Configuration
    SEI_RPC_URL: str = os.getenv("SEI_RPC_URL", "https://evm-rpc.sei-apis.com")
    SEI_STAKING_CONTRACT: str = os.getenv("SEI_STAKING_CONTRACT", "")
    SEI_GOVERNANCE_CONTRACT: str = os.getenv("SEI_GOVERNANCE_CONTRACT", "")
    SEI_STAKING_ABI: str = os.getenv("SEI_STAKING_ABI", "abis/sei-staking-precompile.json")
    SEI_GOVERNANCE_ABI: str = os.getenv("SEI_GOVERNANCE_ABI", "abis/sei-governance-precompile.json")
    
    # Ethereum Configuration
    ETHEREUM_RPC: str = os.getenv("ETHEREUM_RPC", "")
    ETHERSCAN_API_KEY: str = os.getenv("ETHERSCAN_API_KEY", "")
    
    # Solana Configuration
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "")
    SOLANA_WS_URL: str = os.getenv("SOLANA_WS_URL", "")
    
    # ML Configuration
    MODEL_S3_BUCKET: str = os.getenv("MODEL_S3_BUCKET", "")
    MODEL_S3_KEY: str = os.getenv("MODEL_S3_KEY", "")
    
    # API Configuration
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))

config = Config()

class ProductionCreditTracker:
    """Production credit tracking service with multichain support"""
    
    def __init__(self):
        self.app = FastAPI(
            title="DeFi Credit Tracker API",
            description="Production-ready DeFi credit scoring with multichain support",
            version="2.0.0"
        )
        self.setup_cors()
        self.setup_routes()
        
        # Initialize connections
        self.redis_client = None
        self.sei_staking_service = None
        self.sei_governance_service = None
        self.credit_scorer = None
        
        # ML model state
        self.model_version = "v1.0.0"
        self.model_loaded_at = int(time.time())
        self.price_sources_ok = True
        
        # Rate limiting
        self.request_counts = {}
    
    def setup_cors(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    async def startup(self):
        """Initialize all connections and services"""
        try:
            # Redis connection
            self.redis_client = redis.Redis.from_url(config.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis connected successfully")
            
            # Initialize SEI services
            self.sei_staking_service = SEIStakingService(redis_client=self.redis_client)
            self.sei_governance_service = SEIGovernanceService(redis_client=self.redis_client)
            
            # Initialize credit scorer
            self.credit_scorer = DeFiCreditScorer(
                lending_pool_addr="0xA1b2C3d4E5f678901234567890abcdef12345678",
                abi_path="yei-pool.json",
                redis_client=self.redis_client
            )
            
            logger.info("Production Credit Tracker startup complete")
            
        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise
    
    async def check_rate_limit(self, client_ip: str) -> bool:
        """Check rate limiting for client IP"""
        current_time = int(time.time())
        minute_key = f"rate_limit:{client_ip}:{current_time // 60}"
        
        try:
            current_count = await self.redis_client.get(minute_key)
            if current_count and int(current_count) >= config.RATE_LIMIT_PER_MINUTE:
                return False
            
            # Increment counter
            await self.redis_client.incr(minute_key)
            await self.redis_client.expire(minute_key, 60)  # Expire after 1 minute
            return True
            
        except Exception as e:
            logger.warning(f"Rate limit check failed: {e}")
            return True  # Allow request if rate limiting fails
    
    async def get_credit_score(self, wallet: str, chain: str = "sei", client_ip: str = "unknown") -> CreditScoreResponse:
        """
        Get credit score for a wallet on specified chain
        
        Args:
            wallet: Wallet address
            chain: Blockchain (sei, eth, sol)
            client_ip: Client IP for rate limiting
            
        Returns:
            CreditScoreResponse with score and factors
        """
        start_time = time.time()
        
        # Check rate limit
        if not await self.check_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Validate wallet format based on chain
        if not self._validate_wallet_format(wallet, chain):
            raise HTTPException(status_code=400, detail=f"Invalid {chain} wallet format")
        
        # Check cache first
        cache_key = f"credit_score:{chain}:{wallet.lower()}"
        if self.redis_client:
            try:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    cached_data = json.loads(cached)
                    if time.time() - cached_data.get('timestamp', 0) < config.CACHE_TTL_SECONDS:
                        logger.info(f"Using cached credit score for {wallet}")
                        cached_data['latency_ms'] = int((time.time() - start_time) * 1000)
                        return CreditScoreResponse(**cached_data)
            except Exception as e:
                logger.warning(f"Cache error: {e}")
        
        try:
            # Get credit score based on chain
            if chain == "sei":
                score_data = await self._get_sei_credit_score(wallet)
            elif chain == "eth":
                score_data = await self._get_ethereum_credit_score(wallet)
            elif chain == "sol":
                score_data = await self._get_solana_credit_score(wallet)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported chain: {chain}")
            
            # Add metadata
            score_data['latency_ms'] = int((time.time() - start_time) * 1000)
            score_data['model_version'] = self.model_version
            score_data['last_updated'] = int(time.time())
            
            # Cache the result
            if self.redis_client:
                try:
                    cache_data = {**score_data, 'timestamp': time.time()}
                    await self.redis_client.setex(
                        cache_key, 
                        config.CACHE_TTL_SECONDS, 
                        json.dumps(cache_data)
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache credit score: {e}")
            
            return CreditScoreResponse(**score_data)
            
        except Exception as e:
            logger.error(f"Error getting credit score for {wallet} on {chain}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _validate_wallet_format(self, wallet: str, chain: str) -> bool:
        """Validate wallet address format for different chains"""
        if chain == "sei" or chain == "eth":
            # Ethereum-style addresses
            return wallet.startswith("0x") and len(wallet) == 42
        elif chain == "sol":
            # Solana addresses are base58 encoded
            return len(wallet) >= 32 and len(wallet) <= 44
        return False
    
    async def _get_sei_credit_score(self, wallet: str) -> Dict[str, Any]:
        """Get SEI credit score with enhanced staking/governance data"""
        try:
            # Get credit score using enhanced scorer
            result = await self.credit_scorer.calculate_async(wallet)
            
            # Get additional SEI-specific data
            staking_metrics = await self.sei_staking_service.get_staking_metrics(wallet)
            governance_metrics = await self.sei_governance_service.get_governance_metrics(wallet)
            
            # Enhance factors with detailed metrics
            enhanced_factors = {
                **result.factors,
                "staking_details": {
                    "bonded_amount": staking_metrics.bonded_amount,
                    "active_epochs": staking_metrics.active_epochs,
                    "total_rewards": staking_metrics.total_rewards,
                    "delegation_count": staking_metrics.delegation_count,
                    "staking_duration_days": staking_metrics.staking_duration_days,
                },
                "governance_details": {
                    "total_votes_cast": governance_metrics.total_votes_cast,
                    "proposals_participated": governance_metrics.proposals_participated,
                    "recent_votes_90d": governance_metrics.recent_votes_90d,
                    "participation_rate": governance_metrics.participation_rate,
                }
            }
            
            return {
                "wallet": result.wallet,
                "chain": "sei",
                "score": result.score,
                "risk": result.risk,
                "confidence": result.confidence,
                "factors": enhanced_factors,
            }
            
        except Exception as e:
            logger.error(f"Error getting SEI credit score: {e}")
            raise
    
    async def _get_ethereum_credit_score(self, wallet: str) -> Dict[str, Any]:
        """Get Ethereum credit score (placeholder for future implementation)"""
        # TODO: Implement Ethereum credit scoring
        # For now, return a basic score
        return {
            "wallet": wallet,
            "chain": "eth",
            "score": 650,
            "risk": "Medium Risk",
            "confidence": 0.7,
            "factors": {
                "Account Age": 20,
                "Tx Activity": 30,
                "Balances": 25,
                "DeFi Extras": 15,
                "Staking": 0,
                "Governance": 0,
            },
        }
    
    async def _get_solana_credit_score(self, wallet: str) -> Dict[str, Any]:
        """Get Solana credit score (placeholder for future implementation)"""
        # TODO: Implement Solana credit scoring
        # For now, return a basic score
        return {
            "wallet": wallet,
            "chain": "sol",
            "score": 600,
            "risk": "Medium Risk",
            "confidence": 0.6,
            "factors": {
                "Account Age": 15,
                "Tx Activity": 25,
                "Balances": 20,
                "DeFi Extras": 10,
                "Staking": 0,
                "Governance": 0,
            },
        }
    
    async def health_check(self) -> HealthResponse:
        """Health check endpoint with service status"""
        try:
            # Check Redis connection
            redis_ok = "connected" if self.redis_client else "disconnected"
            try:
                await self.redis_client.ping()
                redis_ok = "connected"
            except:
                redis_ok = "error"
            
            # Check SEI services
            sei_services_ok = "connected"
            try:
                if self.sei_staking_service and self.sei_governance_service:
                    sei_services_ok = "connected"
                else:
                    sei_services_ok = "disconnected"
            except:
                sei_services_ok = "error"
            
            return HealthResponse(
                status="healthy",
                timestamp=int(time.time()),
                version="2.0.0",
                services={
                    "redis": redis_ok,
                    "sei_services": sei_services_ok,
                    "credit_scorer": "connected" if self.credit_scorer else "disconnected",
                },
                model_version=self.model_version,
                last_loaded_at=self.model_loaded_at,
                price_sources_ok=self.price_sources_ok,
            )
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return HealthResponse(
                status="unhealthy",
                timestamp=int(time.time()),
                version="2.0.0",
                services={"error": str(e)},
                model_version=self.model_version,
                last_loaded_at=self.model_loaded_at,
                price_sources_ok=False,
            )
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            await self.startup()
        
        @self.app.get("/v1/score/{wallet}", response_model=CreditScoreResponse)
        async def get_credit_score_v1(
            request: Request,
            wallet: str,
            chain: str = "sei",
        ):
            """Get credit score for a wallet (v1 API)"""
            try:
                payload = CreditScoreRequest(wallet=wallet, chain=chain)
            except ValidationError as exc:
                raise HTTPException(status_code=422, detail=exc.errors()) from exc

            client_ip = request.client.host if request.client else "unknown"
            return await self.get_credit_score(payload.wallet, payload.chain, client_ip)

        @self.app.post("/v1/score", response_model=CreditScoreResponse)
        async def get_credit_score_post(
            request: Request,
            payload: CreditScoreRequest,
        ):
            """Get credit score via POST request"""
            client_ip = request.client.host if request.client else "unknown"
            return await self.get_credit_score(payload.wallet, payload.chain, client_ip)
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return await self.health_check()
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information"""
            return {
                "message": "DeFi Credit Tracker API v2.0.0",
                "endpoints": {
                    "credit_score": "/v1/score/{wallet}?chain={sei|eth|sol}",
                    "health": "/health",
                    "docs": "/docs"
                },
                "supported_chains": ["sei", "eth", "sol"],
                "version": "2.0.0"
            }
        
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            """Global exception handler"""
            logger.error(f"Unhandled exception: {exc}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "detail": str(exc)}
            )

# Initialize the application
tracker = ProductionCreditTracker()
app = tracker.app

if __name__ == "__main__":
    uvicorn.run(
        "production_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        workers=4
    )
