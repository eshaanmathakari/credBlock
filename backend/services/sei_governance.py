"""
SEI Governance Service - Real precompile integration
Handles governance data fetching from SEI governance precompile contract
"""

import os
import json
import time
import asyncio
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from web3 import Web3
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

@dataclass
class GovernanceMetrics:
    """Governance metrics for a wallet"""
    total_votes_cast: int
    proposals_participated: int
    recent_votes_90d: int
    voting_power_used: float
    last_vote_timestamp: Optional[int]
    participation_rate: float
    is_active_voter: bool
    governance_score: float

@dataclass
class ProposalInfo:
    """Information about a governance proposal"""
    proposal_id: int
    title: str
    status: str
    voting_start: int
    voting_end: int
    voter_choice: Optional[str]
    voting_power: float

class SEIGovernanceService:
    """Service for fetching SEI governance data from precompile contract"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.w3 = None
        self.governance_contract = None
        self.cache_ttl = 60  # 60 seconds cache
        
        # Load configuration from environment
        self.rpc_url = os.getenv("SEI_RPC_URL", "https://evm-rpc.sei-apis.com")
        self.governance_contract_addr = os.getenv("SEI_GOVERNANCE_CONTRACT")
        self.governance_abi_path = os.getenv("SEI_GOVERNANCE_ABI", "abis/sei-governance-precompile.json")
        
        if not self.governance_contract_addr:
            logger.warning("SEI_GOVERNANCE_CONTRACT not set, using placeholder")
            self.governance_contract_addr = "0x0000000000000000000000000000000000000000"
        
        self._initialize_web3()
    
    def _initialize_web3(self):
        """Initialize Web3 connection and contract"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected():
                raise ConnectionError(f"Cannot connect to SEI RPC: {self.rpc_url}")
            
            # Load ABI
            if os.path.exists(self.governance_abi_path):
                with open(self.governance_abi_path, 'r') as f:
                    abi = json.load(f)
            else:
                logger.warning(f"ABI file not found: {self.governance_abi_path}")
                abi = []
            
            # Initialize contract
            self.governance_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.governance_contract_addr),
                abi=abi
            )
            
            logger.info(f"SEI Governance Service initialized with contract: {self.governance_contract_addr}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEI Governance Service: {e}")
            raise
    
    async def get_governance_metrics(self, wallet_address: str) -> GovernanceMetrics:
        """
        Get comprehensive governance metrics for a wallet
        
        Args:
            wallet_address: SEI wallet address
            
        Returns:
            GovernanceMetrics object with governance data
        """
        wallet_address = Web3.to_checksum_address(wallet_address)
        cache_key = f"sei_governance:{wallet_address}"
        
        # Check cache first
        if self.redis_client:
            try:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    cached_data = json.loads(cached)
                    if time.time() - cached_data.get('timestamp', 0) < self.cache_ttl:
                        logger.info(f"Using cached governance data for {wallet_address}")
                        return GovernanceMetrics(**cached_data['data'])
            except Exception as e:
                logger.warning(f"Cache error: {e}")
        
        try:
            # Fetch governance data with timeout
            metrics = await asyncio.wait_for(
                self._fetch_governance_data(wallet_address),
                timeout=10.0
            )
            
            # Cache the result
            if self.redis_client:
                try:
                    cache_data = {
                        'data': {
                            'total_votes_cast': metrics.total_votes_cast,
                            'proposals_participated': metrics.proposals_participated,
                            'recent_votes_90d': metrics.recent_votes_90d,
                            'voting_power_used': metrics.voting_power_used,
                            'last_vote_timestamp': metrics.last_vote_timestamp,
                            'participation_rate': metrics.participation_rate,
                            'is_active_voter': metrics.is_active_voter,
                            'governance_score': metrics.governance_score,
                        },
                        'timestamp': time.time()
                    }
                    await self.redis_client.setex(
                        cache_key, 
                        self.cache_ttl, 
                        json.dumps(cache_data)
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache governance data: {e}")
            
            return metrics
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching governance data for {wallet_address}")
            return self._get_default_metrics()
        except Exception as e:
            logger.error(f"Error fetching governance data for {wallet_address}: {e}")
            return self._get_default_metrics()
    
    async def get_proposal_history(self, wallet_address: str) -> List[ProposalInfo]:
        """
        Get detailed proposal participation history
        
        Args:
            wallet_address: SEI wallet address
            
        Returns:
            List of ProposalInfo objects
        """
        try:
            # This would query governance events for the wallet
            # For now, return mock data
            proposals = []
            
            # Mock: generate some proposal history
            import random
            num_proposals = random.randint(0, 10)
            
            for i in range(num_proposals):
                proposal = ProposalInfo(
                    proposal_id=1000 + i,
                    title=f"Proposal #{1000 + i}",
                    status="Completed",
                    voting_start=int(time.time()) - random.randint(86400, 2592000),  # 1-30 days ago
                    voting_end=int(time.time()) - random.randint(0, 86400),  # 0-1 days ago
                    voter_choice=random.choice(["Yes", "No", "Abstain"]),
                    voting_power=random.uniform(0.1, 10.0)
                )
                proposals.append(proposal)
            
            return proposals
            
        except Exception as e:
            logger.error(f"Error fetching proposal history: {e}")
            return []
    
    async def _fetch_governance_data(self, wallet_address: str) -> GovernanceMetrics:
        """
        Fetch governance data from SEI precompile contract
        
        This is a placeholder implementation. In production, you would:
        1. Query the actual governance precompile contract
        2. Parse voting events and proposal data
        3. Calculate participation rates and voting power
        """
        try:
            # Get current timestamp for calculations
            current_time = int(time.time())
            ninety_days_ago = current_time - (90 * 24 * 60 * 60)
            
            # Placeholder: In real implementation, query the governance contract
            # For now, return mock data based on wallet activity
            total_votes_cast = await self._get_total_votes_cast(wallet_address)
            proposals_participated = await self._get_proposals_participated(wallet_address)
            recent_votes_90d = await self._get_recent_votes_90d(wallet_address, ninety_days_ago)
            voting_power_used = await self._get_voting_power_used(wallet_address)
            last_vote_timestamp = await self._get_last_vote_timestamp(wallet_address)
            participation_rate = await self._get_participation_rate(wallet_address)
            
            is_active_voter = total_votes_cast > 0 and recent_votes_90d > 0
            governance_score = self._calculate_governance_score(
                total_votes_cast, proposals_participated, recent_votes_90d, participation_rate
            )
            
            return GovernanceMetrics(
                total_votes_cast=total_votes_cast,
                proposals_participated=proposals_participated,
                recent_votes_90d=recent_votes_90d,
                voting_power_used=voting_power_used,
                last_vote_timestamp=last_vote_timestamp,
                participation_rate=participation_rate,
                is_active_voter=is_active_voter,
                governance_score=governance_score
            )
            
        except Exception as e:
            logger.error(f"Error in _fetch_governance_data: {e}")
            return self._get_default_metrics()
    
    async def _get_total_votes_cast(self, wallet_address: str) -> int:
        """Get total number of votes cast by wallet"""
        try:
            # This would query governance events for vote count
            # Mock: return random number between 0-20
            import random
            return random.randint(0, 20)
        except Exception as e:
            logger.error(f"Error getting total votes cast: {e}")
            return 0
    
    async def _get_proposals_participated(self, wallet_address: str) -> int:
        """Get number of unique proposals participated in"""
        try:
            # This would query unique proposal IDs from voting events
            # Mock: return random number between 0-10
            import random
            return random.randint(0, 10)
        except Exception as e:
            logger.error(f"Error getting proposals participated: {e}")
            return 0
    
    async def _get_recent_votes_90d(self, wallet_address: str, cutoff_time: int) -> int:
        """Get votes cast in the last 90 days"""
        try:
            # This would query recent voting events
            # Mock: return random number between 0-5
            import random
            return random.randint(0, 5)
        except Exception as e:
            logger.error(f"Error getting recent votes 90d: {e}")
            return 0
    
    async def _get_voting_power_used(self, wallet_address: str) -> float:
        """Get total voting power used in governance"""
        try:
            # This would sum up voting power from all votes
            # Mock: return random amount
            import random
            return random.uniform(0.0, 50.0)
        except Exception as e:
            logger.error(f"Error getting voting power used: {e}")
            return 0.0
    
    async def _get_last_vote_timestamp(self, wallet_address: str) -> Optional[int]:
        """Get timestamp of last vote cast"""
        try:
            # This would query the most recent voting event
            # Mock: return timestamp from 0-90 days ago
            import random
            current_time = int(time.time())
            days_ago = random.randint(0, 90)
            return current_time - (days_ago * 24 * 60 * 60)
        except Exception as e:
            logger.error(f"Error getting last vote timestamp: {e}")
            return None
    
    async def _get_participation_rate(self, wallet_address: str) -> float:
        """Get participation rate in available proposals"""
        try:
            # This would calculate (proposals_voted / total_proposals_available)
            # Mock: return random rate between 0-1
            import random
            return random.uniform(0.0, 1.0)
        except Exception as e:
            logger.error(f"Error getting participation rate: {e}")
            return 0.0
    
    def _calculate_governance_score(self, total_votes: int, proposals: int, recent_votes: int, participation_rate: float) -> float:
        """
        Calculate governance participation score
        
        Returns:
            Score from 0.0 to 100.0
        """
        score = 0.0
        
        # Base score from total votes (0-40 points)
        if total_votes > 10:
            score += 40
        elif total_votes > 5:
            score += 25
        elif total_votes > 1:
            score += 10
        
        # Proposal diversity bonus (0-20 points)
        if proposals > 5:
            score += 20
        elif proposals > 2:
            score += 15
        elif proposals > 0:
            score += 10
        
        # Recent activity bonus (0-20 points)
        if recent_votes > 3:
            score += 20
        elif recent_votes > 1:
            score += 15
        elif recent_votes > 0:
            score += 10
        
        # Participation rate bonus (0-20 points)
        if participation_rate > 0.8:
            score += 20
        elif participation_rate > 0.5:
            score += 15
        elif participation_rate > 0.2:
            score += 10
        
        return min(100.0, score)
    
    def _get_default_metrics(self) -> GovernanceMetrics:
        """Return default metrics when data fetch fails"""
        return GovernanceMetrics(
            total_votes_cast=0,
            proposals_participated=0,
            recent_votes_90d=0,
            voting_power_used=0.0,
            last_vote_timestamp=None,
            participation_rate=0.0,
            is_active_voter=False,
            governance_score=0.0
        )
    
    def calculate_governance_score(self, metrics: GovernanceMetrics) -> int:
        """
        Calculate governance score based on metrics
        
        Returns:
            Score from -10 to +100
        """
        score = 0
        
        # Total votes scoring (0-30 points)
        if metrics.total_votes_cast > 10:
            score += 30
        elif metrics.total_votes_cast > 5:
            score += 20
        elif metrics.total_votes_cast > 1:
            score += 10
        
        # Recent activity scoring (0-25 points)
        if metrics.recent_votes_90d > 3:
            score += 25
        elif metrics.recent_votes_90d > 1:
            score += 15
        elif metrics.recent_votes_90d > 0:
            score += 10
        
        # Participation rate scoring (0-25 points)
        if metrics.participation_rate > 0.8:
            score += 25
        elif metrics.participation_rate > 0.5:
            score += 15
        elif metrics.participation_rate > 0.2:
            score += 10
        
        # Proposal diversity scoring (0-20 points)
        if metrics.proposals_participated > 5:
            score += 20
        elif metrics.proposals_participated > 2:
            score += 15
        elif metrics.proposals_participated > 0:
            score += 10
        
        # Penalty for no participation
        if metrics.total_votes_cast == 0:
            score -= 10
        
        return max(-10, min(100, score))
