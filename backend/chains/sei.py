"""
SEI Chain Adapter
Implements the ChainAdapter interface for SEI blockchain
"""

import os
import time
import asyncio
from typing import Dict, List, Any, Optional
from web3 import Web3
import logging

from .base import (
    ChainAdapter, ChainType, WalletProfile, StakingMetrics, 
    GovernanceMetrics, ProtocolInteraction, TokenBalance
)
from ..services.sei_staking import SEIStakingService
from ..services.sei_governance import SEIGovernanceService
from ..credit_scorer import DeFiCreditScorer
from ..coin_balance import get_wallet_balance

logger = logging.getLogger(__name__)

class SEIAdapter(ChainAdapter):
    """SEI blockchain adapter implementation"""
    
    def __init__(self, chain_type: ChainType, rpc_url: str):
        super().__init__(chain_type, rpc_url)
        self.w3 = None
        self.staking_service = None
        self.governance_service = None
        self.credit_scorer = None
        
        # SEI-specific configuration
        self.explorer_url = "https://sei.blockscout.com/api/v2/addresses"
        self.staking_contract_addr = os.getenv("SEI_STAKING_CONTRACT", "")
        self.governance_contract_addr = os.getenv("SEI_GOVERNANCE_CONTRACT", "")
    
    async def connect(self) -> bool:
        """Connect to SEI RPC"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected():
                raise ConnectionError(f"Cannot connect to SEI RPC: {self.rpc_url}")
            
            # Initialize services
            self.staking_service = SEIStakingService()
            self.governance_service = SEIGovernanceService()
            
            # Initialize credit scorer
            self.credit_scorer = DeFiCreditScorer(
                lending_pool_addr="0xA1b2C3d4E5f678901234567890abcdef12345678",
                abi_path="yei-pool.json"
            )
            
            self.is_connected = True
            logger.info(f"Connected to SEI RPC: {self.rpc_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SEI RPC: {e}")
            self.is_connected = False
            return False
    
    def validate_address(self, address: str) -> bool:
        """Validate SEI wallet address format"""
        try:
            # SEI uses Ethereum-style addresses
            if not address.startswith("0x"):
                return False
            
            # Check length
            if len(address) != 42:
                return False
            
            # Validate checksum
            Web3.to_checksum_address(address)
            return True
            
        except Exception:
            return False
    
    async def get_wallet_profile(self, address: str) -> WalletProfile:
        """Get comprehensive SEI wallet profile"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Validate address
            if not self.validate_address(address):
                raise ValueError(f"Invalid SEI address: {address}")
            
            # Get basic wallet data
            balance_native = get_wallet_balance(address)
            balance_usd = balance_native * 0.5  # Mock USD conversion
            
            # Get transaction count and history
            transaction_count = await self._get_transaction_count(address)
            first_tx_ts, last_tx_ts = await self._get_tx_timestamps(address)
            unique_addresses = await self._get_unique_addresses(address)
            
            # Check if it's a contract
            is_contract = await self._is_contract(address)
            
            # Get credit score for risk assessment
            credit_result = await self.credit_scorer.calculate_async(address)
            risk_score = 1.0 - (credit_result.score / 1000)  # Invert score to risk
            confidence = credit_result.confidence
            
            return WalletProfile(
                address=address,
                chain=self.chain_type,
                balance_native=balance_native,
                balance_usd=balance_usd,
                transaction_count=transaction_count,
                first_tx_timestamp=first_tx_ts,
                last_tx_timestamp=last_tx_ts,
                unique_addresses=unique_addresses,
                is_contract=is_contract,
                risk_score=risk_score,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error getting SEI wallet profile for {address}: {e}")
            # Return default profile
            return WalletProfile(
                address=address,
                chain=self.chain_type,
                balance_native=0.0,
                balance_usd=0.0,
                transaction_count=0,
                first_tx_timestamp=None,
                last_tx_timestamp=None,
                unique_addresses=0,
                is_contract=False,
                risk_score=0.5,
                confidence=0.5
            )
    
    async def get_staking_metrics(self, address: str) -> StakingMetrics:
        """Get SEI staking metrics"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Get staking data from service
            staking_data = await self.staking_service.get_staking_metrics(address)
            
            return StakingMetrics(
                total_staked=staking_data.bonded_amount,
                staking_duration_days=staking_data.staking_duration_days,
                rewards_earned=staking_data.total_rewards,
                penalties_incurred=staking_data.slashing_penalties,
                validator_count=staking_data.delegation_count,
                is_active_staker=staking_data.is_active_staker,
                staking_score=staking_data.bonded_amount / 1000.0  # Normalize to 0-1
            )
            
        except Exception as e:
            logger.error(f"Error getting SEI staking metrics for {address}: {e}")
            return StakingMetrics(
                total_staked=0.0,
                staking_duration_days=0,
                rewards_earned=0.0,
                penalties_incurred=0.0,
                validator_count=0,
                is_active_staker=False,
                staking_score=0.0
            )
    
    async def get_governance_metrics(self, address: str) -> GovernanceMetrics:
        """Get SEI governance metrics"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Get governance data from service
            governance_data = await self.governance_service.get_governance_metrics(address)
            
            return GovernanceMetrics(
                total_votes_cast=governance_data.total_votes_cast,
                proposals_participated=governance_data.proposals_participated,
                recent_votes_90d=governance_data.recent_votes_90d,
                voting_power_used=governance_data.voting_power_used,
                participation_rate=governance_data.participation_rate,
                is_active_voter=governance_data.is_active_voter,
                governance_score=governance_data.governance_score / 100.0  # Normalize to 0-1
            )
            
        except Exception as e:
            logger.error(f"Error getting SEI governance metrics for {address}: {e}")
            return GovernanceMetrics(
                total_votes_cast=0,
                proposals_participated=0,
                recent_votes_90d=0,
                voting_power_used=0.0,
                participation_rate=0.0,
                is_active_voter=False,
                governance_score=0.0
            )
    
    async def get_protocol_interactions(self, address: str) -> List[ProtocolInteraction]:
        """Get SEI protocol interactions"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # For now, return mock data
            # In production, this would query protocol events and interactions
            interactions = []
            
            # Mock lending protocol interaction
            interactions.append(ProtocolInteraction(
                protocol_name="YEI Lending",
                protocol_type="lending",
                total_volume_usd=1000.0,
                interaction_count=5,
                last_interaction_timestamp=int(time.time()) - 86400 * 7,  # 7 days ago
                risk_level="low"
            ))
            
            # Mock DEX interaction
            interactions.append(ProtocolInteraction(
                protocol_name="SEI DEX",
                protocol_type="dex",
                total_volume_usd=500.0,
                interaction_count=3,
                last_interaction_timestamp=int(time.time()) - 86400 * 3,  # 3 days ago
                risk_level="medium"
            ))
            
            return interactions
            
        except Exception as e:
            logger.error(f"Error getting SEI protocol interactions for {address}: {e}")
            return []
    
    async def get_token_balances(self, address: str) -> List[TokenBalance]:
        """Get SEI token balances"""
        try:
            if not self.is_connected:
                await self.connect()
            
            balances = []
            
            # Native SEI balance
            native_balance = get_wallet_balance(address)
            balances.append(TokenBalance(
                token_address="0x0000000000000000000000000000000000000000",
                token_symbol="SEI",
                balance_raw=str(int(native_balance * 1e18)),
                balance_formatted=native_balance,
                value_usd=native_balance * 0.5,  # Mock USD price
                price_usd=0.5,
                is_stablecoin=False,
                is_bluechip=True
            ))
            
            # Mock USDC balance
            balances.append(TokenBalance(
                token_address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                token_symbol="USDC",
                balance_raw="1000000000",  # 1000 USDC
                balance_formatted=1000.0,
                value_usd=1000.0,
                price_usd=1.0,
                is_stablecoin=True,
                is_bluechip=True
            ))
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting SEI token balances for {address}: {e}")
            return []
    
    async def get_transaction_history(self, address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get SEI transaction history"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # For now, return mock data
            # In production, this would query the SEI explorer API
            transactions = []
            
            for i in range(min(limit, 10)):
                transactions.append({
                    'hash': f"0x{'a' * 64}",
                    'block_number': 1000000 + i,
                    'timestamp': int(time.time()) - 86400 * i,
                    'from': address,
                    'to': f"0x{'b' * 40}",
                    'value': "1000000000000000000",  # 1 SEI
                    'gas_used': 21000,
                    'gas_price': "20000000000",
                    'status': 1
                })
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting SEI transaction history for {address}: {e}")
            return []
    
    async def get_credit_score_factors(self, address: str) -> Dict[str, Any]:
        """Get SEI credit score factors"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Get credit score using existing scorer
            credit_result = await self.credit_scorer.calculate_async(address)
            
            # Get additional metrics
            staking_metrics = await self.get_staking_metrics(address)
            governance_metrics = await self.get_governance_metrics(address)
            
            return {
                'score': credit_result.score,
                'risk': credit_result.risk,
                'confidence': credit_result.confidence,
                'factors': credit_result.factors,
                'staking_metrics': {
                    'total_staked': staking_metrics.total_staked,
                    'staking_duration_days': staking_metrics.staking_duration_days,
                    'is_active_staker': staking_metrics.is_active_staker,
                },
                'governance_metrics': {
                    'total_votes_cast': governance_metrics.total_votes_cast,
                    'participation_rate': governance_metrics.participation_rate,
                    'is_active_voter': governance_metrics.is_active_voter,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting SEI credit score factors for {address}: {e}")
            return {
                'score': 500,
                'risk': 'Medium Risk',
                'confidence': 0.5,
                'factors': {},
                'staking_metrics': {},
                'governance_metrics': {}
            }
    
    async def _get_transaction_count(self, address: str) -> int:
        """Get transaction count for address"""
        try:
            # Mock implementation - in production would query explorer API
            return 50
        except Exception as e:
            logger.error(f"Error getting transaction count: {e}")
            return 0
    
    async def _get_tx_timestamps(self, address: str) -> tuple[Optional[int], Optional[int]]:
        """Get first and last transaction timestamps"""
        try:
            # Mock implementation
            current_time = int(time.time())
            first_tx = current_time - 86400 * 30  # 30 days ago
            last_tx = current_time - 86400  # 1 day ago
            return first_tx, last_tx
        except Exception as e:
            logger.error(f"Error getting transaction timestamps: {e}")
            return None, None
    
    async def _get_unique_addresses(self, address: str) -> int:
        """Get number of unique addresses interacted with"""
        try:
            # Mock implementation
            return 20
        except Exception as e:
            logger.error(f"Error getting unique addresses: {e}")
            return 0
    
    async def _is_contract(self, address: str) -> bool:
        """Check if address is a contract"""
        try:
            if not self.w3:
                return False
            
            code = self.w3.eth.get_code(address)
            return code != b''
        except Exception as e:
            logger.error(f"Error checking if address is contract: {e}")
            return False


# Register the SEI adapter with the factory
from .base import ChainAdapterFactory
ChainAdapterFactory.register_adapter(ChainType.SEI, SEIAdapter)
