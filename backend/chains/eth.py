"""
Ethereum Chain Adapter
Implements the ChainAdapter interface for Ethereum blockchain
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

logger = logging.getLogger(__name__)

class EthereumAdapter(ChainAdapter):
    """Ethereum blockchain adapter implementation"""
    
    def __init__(self, chain_type: ChainType, rpc_url: str):
        super().__init__(chain_type, rpc_url)
        self.w3 = None
        self.etherscan_api_key = os.getenv("ETHERSCAN_API_KEY", "")
    
    async def connect(self) -> bool:
        """Connect to Ethereum RPC"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected():
                raise ConnectionError(f"Cannot connect to Ethereum RPC: {self.rpc_url}")
            
            self.is_connected = True
            logger.info(f"Connected to Ethereum RPC: {self.rpc_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Ethereum RPC: {e}")
            self.is_connected = False
            return False
    
    def validate_address(self, address: str) -> bool:
        """Validate Ethereum wallet address format"""
        try:
            # Ethereum addresses start with 0x and are 42 characters long
            if not address.startswith("0x"):
                return False
            
            if len(address) != 42:
                return False
            
            # Validate checksum
            Web3.to_checksum_address(address)
            return True
            
        except Exception:
            return False
    
    async def get_wallet_profile(self, address: str) -> WalletProfile:
        """Get comprehensive Ethereum wallet profile"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Validate address
            if not self.validate_address(address):
                raise ValueError(f"Invalid Ethereum address: {address}")
            
            # Get ETH balance
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            balance_usd = float(balance_eth) * 2000  # Mock ETH price
            
            # Mock transaction data
            transaction_count = 150
            first_tx_ts = int(time.time()) - 86400 * 365  # 1 year ago
            last_tx_ts = int(time.time()) - 86400 * 7  # 1 week ago
            unique_addresses = 45
            
            # Check if it's a contract
            is_contract = await self._is_contract(address)
            
            # Mock risk assessment
            risk_score = 0.3  # Low risk for demo
            confidence = 0.8
            
            return WalletProfile(
                address=address,
                chain=self.chain_type,
                balance_native=float(balance_eth),
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
            logger.error(f"Error getting Ethereum wallet profile for {address}: {e}")
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
        """Get Ethereum staking metrics (Lido, Rocket Pool, etc.)"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock staking data
            # In production, this would query Lido, Rocket Pool, and other staking protocols
            return StakingMetrics(
                total_staked=5.0,  # 5 ETH staked
                staking_duration_days=180,
                rewards_earned=0.2,  # 0.2 ETH rewards
                penalties_incurred=0.0,
                validator_count=1,
                is_active_staker=True,
                staking_score=0.7
            )
            
        except Exception as e:
            logger.error(f"Error getting Ethereum staking metrics for {address}: {e}")
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
        """Get Ethereum governance metrics (Compound, Aave, etc.)"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock governance data
            # In production, this would query Compound, Aave, and other governance protocols
            return GovernanceMetrics(
                total_votes_cast=8,
                proposals_participated=5,
                recent_votes_90d=3,
                voting_power_used=100.0,
                participation_rate=0.6,
                is_active_voter=True,
                governance_score=0.6
            )
            
        except Exception as e:
            logger.error(f"Error getting Ethereum governance metrics for {address}: {e}")
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
        """Get Ethereum protocol interactions"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock protocol interactions
            interactions = []
            
            # Uniswap interaction
            interactions.append(ProtocolInteraction(
                protocol_name="Uniswap V3",
                protocol_type="dex",
                total_volume_usd=5000.0,
                interaction_count=25,
                last_interaction_timestamp=int(time.time()) - 86400 * 2,
                risk_level="low"
            ))
            
            # Aave interaction
            interactions.append(ProtocolInteraction(
                protocol_name="Aave V3",
                protocol_type="lending",
                total_volume_usd=2000.0,
                interaction_count=8,
                last_interaction_timestamp=int(time.time()) - 86400 * 5,
                risk_level="low"
            ))
            
            # Compound interaction
            interactions.append(ProtocolInteraction(
                protocol_name="Compound V3",
                protocol_type="lending",
                total_volume_usd=1500.0,
                interaction_count=6,
                last_interaction_timestamp=int(time.time()) - 86400 * 10,
                risk_level="low"
            ))
            
            return interactions
            
        except Exception as e:
            logger.error(f"Error getting Ethereum protocol interactions for {address}: {e}")
            return []
    
    async def get_token_balances(self, address: str) -> List[TokenBalance]:
        """Get Ethereum token balances"""
        try:
            if not self.is_connected:
                await self.connect()
            
            balances = []
            
            # ETH balance
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            balances.append(TokenBalance(
                token_address="0x0000000000000000000000000000000000000000",
                token_symbol="ETH",
                balance_raw=str(balance_wei),
                balance_formatted=float(balance_eth),
                value_usd=float(balance_eth) * 2000,  # Mock ETH price
                price_usd=2000.0,
                is_stablecoin=False,
                is_bluechip=True
            ))
            
            # Mock USDC balance
            balances.append(TokenBalance(
                token_address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                token_symbol="USDC",
                balance_raw="5000000000",  # 5000 USDC
                balance_formatted=5000.0,
                value_usd=5000.0,
                price_usd=1.0,
                is_stablecoin=True,
                is_bluechip=True
            ))
            
            # Mock USDT balance
            balances.append(TokenBalance(
                token_address="0xdac17f958d2ee523a2206206994597c13d831ec7",
                token_symbol="USDT",
                balance_raw="3000000000",  # 3000 USDT
                balance_formatted=3000.0,
                value_usd=3000.0,
                price_usd=1.0,
                is_stablecoin=True,
                is_bluechip=True
            ))
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting Ethereum token balances for {address}: {e}")
            return []
    
    async def get_transaction_history(self, address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get Ethereum transaction history"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock transaction history
            # In production, this would query Etherscan API or use Web3
            transactions = []
            
            for i in range(min(limit, 20)):
                transactions.append({
                    'hash': f"0x{'a' * 64}",
                    'block_number': 18000000 + i,
                    'timestamp': int(time.time()) - 86400 * i,
                    'from': address,
                    'to': f"0x{'b' * 40}",
                    'value': "1000000000000000000",  # 1 ETH
                    'gas_used': 21000,
                    'gas_price': "20000000000",
                    'status': 1
                })
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting Ethereum transaction history for {address}: {e}")
            return []
    
    async def get_credit_score_factors(self, address: str) -> Dict[str, Any]:
        """Get Ethereum credit score factors"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock credit score calculation
            # In production, this would use ML models trained on Ethereum data
            base_score = 650
            
            # Adjust based on wallet characteristics
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            if float(balance_eth) > 10:
                base_score += 50
            elif float(balance_eth) > 1:
                base_score += 20
            
            # Mock factors
            factors = {
                "Account Age": 30,
                "Tx Activity": 40,
                "Balances": 25,
                "DeFi Extras": 35,
                "Staking": 20,
                "Governance": 15,
            }
            
            return {
                'score': base_score,
                'risk': 'Low Risk' if base_score >= 700 else 'Medium Risk',
                'confidence': 0.8,
                'factors': factors,
                'staking_metrics': {
                    'total_staked': 5.0,
                    'staking_duration_days': 180,
                    'is_active_staker': True,
                },
                'governance_metrics': {
                    'total_votes_cast': 8,
                    'participation_rate': 0.6,
                    'is_active_voter': True,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting Ethereum credit score factors for {address}: {e}")
            return {
                'score': 500,
                'risk': 'Medium Risk',
                'confidence': 0.5,
                'factors': {},
                'staking_metrics': {},
                'governance_metrics': {}
            }
    
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


# Register the Ethereum adapter with the factory
from .base import ChainAdapterFactory
ChainAdapterFactory.register_adapter(ChainType.ETHEREUM, EthereumAdapter)
