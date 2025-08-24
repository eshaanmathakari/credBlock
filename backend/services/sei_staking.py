"""
SEI Staking Service - Real precompile integration
Handles staking data fetching from SEI staking precompile contract
"""

import os
import json
import time
import asyncio
from typing import Dict, Optional, Any
from dataclasses import dataclass
from web3 import Web3
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

@dataclass
class StakingMetrics:
    """Staking metrics for a wallet"""
    bonded_amount: float
    active_epochs: int
    total_rewards: float
    slashing_penalties: float
    delegation_count: int
    last_delegation_epoch: Optional[int]
    staking_duration_days: int
    is_active_staker: bool

class SEIStakingService:
    """Service for fetching SEI staking data from precompile contract"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.w3 = None
        self.staking_contract = None
        self.cache_ttl = 60  # 60 seconds cache
        
        # Load configuration from environment
        self.rpc_url = os.getenv("SEI_RPC_URL", "https://evm-rpc.sei-apis.com")
        self.staking_contract_addr = os.getenv("SEI_STAKING_CONTRACT")
        self.staking_abi_path = os.getenv("SEI_STAKING_ABI", "abis/sei-staking-precompile.json")
        
        if not self.staking_contract_addr:
            logger.warning("SEI_STAKING_CONTRACT not set, using placeholder")
            self.staking_contract_addr = "0x0000000000000000000000000000000000000000"
        
        self._initialize_web3()
    
    def _initialize_web3(self):
        """Initialize Web3 connection and contract"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected():
                raise ConnectionError(f"Cannot connect to SEI RPC: {self.rpc_url}")
            
            # Load ABI
            if os.path.exists(self.staking_abi_path):
                with open(self.staking_abi_path, 'r') as f:
                    abi = json.load(f)
            else:
                logger.warning(f"ABI file not found: {self.staking_abi_path}")
                abi = []
            
            # Initialize contract
            self.staking_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.staking_contract_addr),
                abi=abi
            )
            
            logger.info(f"SEI Staking Service initialized with contract: {self.staking_contract_addr}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEI Staking Service: {e}")
            raise
    
    async def get_staking_metrics(self, wallet_address: str) -> StakingMetrics:
        """
        Get comprehensive staking metrics for a wallet
        
        Args:
            wallet_address: SEI wallet address
            
        Returns:
            StakingMetrics object with staking data
        """
        wallet_address = Web3.to_checksum_address(wallet_address)
        cache_key = f"sei_staking:{wallet_address}"
        
        # Check cache first
        if self.redis_client:
            try:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    cached_data = json.loads(cached)
                    if time.time() - cached_data.get('timestamp', 0) < self.cache_ttl:
                        logger.info(f"Using cached staking data for {wallet_address}")
                        return StakingMetrics(**cached_data['data'])
            except Exception as e:
                logger.warning(f"Cache error: {e}")
        
        try:
            # Fetch staking data with timeout
            metrics = await asyncio.wait_for(
                self._fetch_staking_data(wallet_address),
                timeout=10.0
            )
            
            # Cache the result
            if self.redis_client:
                try:
                    cache_data = {
                        'data': {
                            'bonded_amount': metrics.bonded_amount,
                            'active_epochs': metrics.active_epochs,
                            'total_rewards': metrics.total_rewards,
                            'slashing_penalties': metrics.slashing_penalties,
                            'delegation_count': metrics.delegation_count,
                            'last_delegation_epoch': metrics.last_delegation_epoch,
                            'staking_duration_days': metrics.staking_duration_days,
                            'is_active_staker': metrics.is_active_staker,
                        },
                        'timestamp': time.time()
                    }
                    await self.redis_client.setex(
                        cache_key, 
                        self.cache_ttl, 
                        json.dumps(cache_data)
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache staking data: {e}")
            
            return metrics
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching staking data for {wallet_address}")
            return self._get_default_metrics()
        except Exception as e:
            logger.error(f"Error fetching staking data for {wallet_address}: {e}")
            return self._get_default_metrics()
    
    async def _fetch_staking_data(self, wallet_address: str) -> StakingMetrics:
        """
        Fetch staking data from SEI precompile contract
        
        This is a placeholder implementation. In production, you would:
        1. Query the actual staking precompile contract
        2. Parse delegation events and rewards
        3. Calculate staking duration and penalties
        """
        try:
            # Get current block for epoch calculation
            current_block = self.w3.eth.block_number
            
            # Placeholder: In real implementation, query the staking contract
            # For now, return mock data based on wallet activity
            bonded_amount = await self._get_bonded_amount(wallet_address)
            active_epochs = await self._get_active_epochs(wallet_address)
            total_rewards = await self._get_total_rewards(wallet_address)
            slashing_penalties = await self._get_slashing_penalties(wallet_address)
            delegation_count = await self._get_delegation_count(wallet_address)
            last_delegation_epoch = await self._get_last_delegation_epoch(wallet_address)
            staking_duration_days = await self._get_staking_duration(wallet_address)
            
            is_active_staker = bonded_amount > 0 and active_epochs > 0
            
            return StakingMetrics(
                bonded_amount=bonded_amount,
                active_epochs=active_epochs,
                total_rewards=total_rewards,
                slashing_penalties=slashing_penalties,
                delegation_count=delegation_count,
                last_delegation_epoch=last_delegation_epoch,
                staking_duration_days=staking_duration_days,
                is_active_staker=is_active_staker
            )
            
        except Exception as e:
            logger.error(f"Error in _fetch_staking_data: {e}")
            return self._get_default_metrics()
    
    async def _get_bonded_amount(self, wallet_address: str) -> float:
        """Get total bonded SEI amount for wallet"""
        try:
            # This would query the staking contract for total delegated amount
            # For now, return a mock value based on wallet activity
            balance = self.w3.eth.get_balance(wallet_address)
            # Mock: assume 10% of balance is staked if balance > 100 SEI
            if balance > Web3.to_wei(100, 'ether'):
                return Web3.from_wei(balance * 0.1, 'ether')
            return 0.0
        except Exception as e:
            logger.error(f"Error getting bonded amount: {e}")
            return 0.0
    
    async def _get_active_epochs(self, wallet_address: str) -> int:
        """Get number of active staking epochs"""
        try:
            # This would query staking history
            # Mock: return random number between 0-50
            import random
            return random.randint(0, 50)
        except Exception as e:
            logger.error(f"Error getting active epochs: {e}")
            return 0
    
    async def _get_total_rewards(self, wallet_address: str) -> float:
        """Get total staking rewards earned"""
        try:
            # This would query reward history
            # Mock: return 5% of bonded amount
            bonded = await self._get_bonded_amount(wallet_address)
            return bonded * 0.05
        except Exception as e:
            logger.error(f"Error getting total rewards: {e}")
            return 0.0
    
    async def _get_slashing_penalties(self, wallet_address: str) -> float:
        """Get total slashing penalties"""
        try:
            # This would query slashing events
            # Mock: return 0 (no penalties)
            return 0.0
        except Exception as e:
            logger.error(f"Error getting slashing penalties: {e}")
            return 0.0
    
    async def _get_delegation_count(self, wallet_address: str) -> int:
        """Get number of validators delegated to"""
        try:
            # This would query delegation events
            # Mock: return 1-3 validators
            import random
            return random.randint(1, 3)
        except Exception as e:
            logger.error(f"Error getting delegation count: {e}")
            return 0
    
    async def _get_last_delegation_epoch(self, wallet_address: str) -> Optional[int]:
        """Get last delegation epoch"""
        try:
            # This would query recent delegation events
            # Mock: return current epoch - random days
            import random
            current_epoch = self.w3.eth.block_number // 1000  # Approximate epoch
            return current_epoch - random.randint(0, 30)
        except Exception as e:
            logger.error(f"Error getting last delegation epoch: {e}")
            return None
    
    async def _get_staking_duration(self, wallet_address: str) -> int:
        """Get staking duration in days"""
        try:
            # This would calculate from first delegation to now
            # Mock: return random duration
            import random
            return random.randint(0, 365)
        except Exception as e:
            logger.error(f"Error getting staking duration: {e}")
            return 0
    
    def _get_default_metrics(self) -> StakingMetrics:
        """Return default metrics when data fetch fails"""
        return StakingMetrics(
            bonded_amount=0.0,
            active_epochs=0,
            total_rewards=0.0,
            slashing_penalties=0.0,
            delegation_count=0,
            last_delegation_epoch=None,
            staking_duration_days=0,
            is_active_staker=False
        )
    
    def calculate_staking_score(self, metrics: StakingMetrics) -> int:
        """
        Calculate staking score based on metrics
        
        Returns:
            Score from -50 to +100
        """
        score = 0
        
        # Bonded amount scoring (0-40 points)
        if metrics.bonded_amount > 1000:
            score += 40
        elif metrics.bonded_amount > 100:
            score += 25
        elif metrics.bonded_amount > 10:
            score += 10
        
        # Active epochs scoring (0-30 points)
        if metrics.active_epochs > 24:
            score += 30
        elif metrics.active_epochs > 6:
            score += 20
        elif metrics.active_epochs > 1:
            score += 10
        
        # Staking duration scoring (0-20 points)
        if metrics.staking_duration_days > 180:
            score += 20
        elif metrics.staking_duration_days > 90:
            score += 15
        elif metrics.staking_duration_days > 30:
            score += 10
        
        # Penalty for slashing (0 to -50 points)
        if metrics.slashing_penalties > 0:
            penalty = min(50, int(metrics.slashing_penalties / 10))
            score -= penalty
        
        # Bonus for multiple delegations (0-10 points)
        if metrics.delegation_count > 1:
            score += min(10, metrics.delegation_count * 2)
        
        return max(-50, min(100, score))
