"""
Solana Chain Adapter
Implements the ChainAdapter interface for Solana blockchain
"""

import os
import time
import asyncio
from typing import Dict, List, Any, Optional
import logging

from .base import (
    ChainAdapter, ChainType, WalletProfile, StakingMetrics, 
    GovernanceMetrics, ProtocolInteraction, TokenBalance
)

logger = logging.getLogger(__name__)

class SolanaAdapter(ChainAdapter):
    """Solana blockchain adapter implementation"""
    
    def __init__(self, chain_type: ChainType, rpc_url: str):
        super().__init__(chain_type, rpc_url)
        # In production, this would use solana-py library
        # from solana.rpc.api import Client
        # self.client = Client(rpc_url)
    
    async def connect(self) -> bool:
        """Connect to Solana RPC"""
        try:
            # Mock connection - in production would use solana-py
            # self.client = Client(self.rpc_url)
            # await self.client.get_health()
            
            self.is_connected = True
            logger.info(f"Connected to Solana RPC: {self.rpc_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Solana RPC: {e}")
            self.is_connected = False
            return False
    
    def validate_address(self, address: str) -> bool:
        """Validate Solana wallet address format"""
        try:
            # Solana addresses are base58 encoded and typically 32-44 characters
            if len(address) < 32 or len(address) > 44:
                return False
            
            # Check if it contains only base58 characters
            import base58
            try:
                base58.b58decode(address)
                return True
            except Exception:
                return False
            
        except Exception:
            return False
    
    async def get_wallet_profile(self, address: str) -> WalletProfile:
        """Get comprehensive Solana wallet profile"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Validate address
            if not self.validate_address(address):
                raise ValueError(f"Invalid Solana address: {address}")
            
            # Mock Solana data
            # In production, this would query Solana RPC
            balance_sol = 25.5  # Mock SOL balance
            balance_usd = balance_sol * 100  # Mock SOL price
            
            # Mock transaction data
            transaction_count = 200
            first_tx_ts = int(time.time()) - 86400 * 180  # 6 months ago
            last_tx_ts = int(time.time()) - 86400 * 2  # 2 days ago
            unique_addresses = 60
            
            # Check if it's a program (contract)
            is_contract = False  # Mock - would check program account
            
            # Mock risk assessment
            risk_score = 0.2  # Low risk for demo
            confidence = 0.75
            
            return WalletProfile(
                address=address,
                chain=self.chain_type,
                balance_native=balance_sol,
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
            logger.error(f"Error getting Solana wallet profile for {address}: {e}")
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
        """Get Solana staking metrics"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock staking data
            # In production, this would query stake accounts and validators
            return StakingMetrics(
                total_staked=15.0,  # 15 SOL staked
                staking_duration_days=120,
                rewards_earned=0.8,  # 0.8 SOL rewards
                penalties_incurred=0.0,
                validator_count=3,
                is_active_staker=True,
                staking_score=0.8
            )
            
        except Exception as e:
            logger.error(f"Error getting Solana staking metrics for {address}: {e}")
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
        """Get Solana governance metrics (SPL Governance)"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock governance data
            # In production, this would query SPL Governance programs
            return GovernanceMetrics(
                total_votes_cast=12,
                proposals_participated=8,
                recent_votes_90d=5,
                voting_power_used=250.0,
                participation_rate=0.7,
                is_active_voter=True,
                governance_score=0.7
            )
            
        except Exception as e:
            logger.error(f"Error getting Solana governance metrics for {address}: {e}")
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
        """Get Solana protocol interactions"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock protocol interactions
            interactions = []
            
            # Raydium interaction
            interactions.append(ProtocolInteraction(
                protocol_name="Raydium",
                protocol_type="dex",
                total_volume_usd=8001.0,
                interaction_count=40,
                last_interaction_timestamp=int(time.time()) - 86400 * 1,
                risk_level="low"
            ))
            
            # Orca interaction
            interactions.append(ProtocolInteraction(
                protocol_name="Orca",
                protocol_type="dex",
                total_volume_usd=3000.0,
                interaction_count=15,
                last_interaction_timestamp=int(time.time()) - 86400 * 3,
                risk_level="low"
            ))
            
            # Solend interaction
            interactions.append(ProtocolInteraction(
                protocol_name="Solend",
                protocol_type="lending",
                total_volume_usd=2500.0,
                interaction_count=12,
                last_interaction_timestamp=int(time.time()) - 86400 * 7,
                risk_level="low"
            ))
            
            # Marinade interaction
            interactions.append(ProtocolInteraction(
                protocol_name="Marinade Finance",
                protocol_type="staking",
                total_volume_usd=5000.0,
                interaction_count=8,
                last_interaction_timestamp=int(time.time()) - 86400 * 5,
                risk_level="low"
            ))
            
            return interactions
            
        except Exception as e:
            logger.error(f"Error getting Solana protocol interactions for {address}: {e}")
            return []
    
    async def get_token_balances(self, address: str) -> List[TokenBalance]:
        """Get Solana token balances"""
        try:
            if not self.is_connected:
                await self.connect()
            
            balances = []
            
            # SOL balance
            balances.append(TokenBalance(
                token_address="So11111111111111111111111111111111111111112",
                token_symbol="SOL",
                balance_raw="25500000000",  # 25.5 SOL
                balance_formatted=25.5,
                value_usd=25.5 * 100,  # Mock SOL price
                price_usd=100.0,
                is_stablecoin=False,
                is_bluechip=True
            ))
            
            # USDC balance
            balances.append(TokenBalance(
                token_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                token_symbol="USDC",
                balance_raw="7500000000",  # 7500 USDC
                balance_formatted=7500.0,
                value_usd=7500.0,
                price_usd=1.0,
                is_stablecoin=True,
                is_bluechip=True
            ))
            
            # USDT balance
            balances.append(TokenBalance(
                token_address="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
                token_symbol="USDT",
                balance_raw="4000000000",  # 4000 USDT
                balance_formatted=4000.0,
                value_usd=4000.0,
                price_usd=1.0,
                is_stablecoin=True,
                is_bluechip=True
            ))
            
            # mSOL balance (Marinade staked SOL)
            balances.append(TokenBalance(
                token_address="mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
                token_symbol="mSOL",
                balance_raw="15000000000",  # 15 mSOL
                balance_formatted=15.0,
                value_usd=15.0 * 100,
                price_usd=100.0,
                is_stablecoin=False,
                is_bluechip=False
            ))
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting Solana token balances for {address}: {e}")
            return []
    
    async def get_transaction_history(self, address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get Solana transaction history"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock transaction history
            # In production, this would query Solana RPC
            transactions = []
            
            for i in range(min(limit, 25)):
                transactions.append({
                    'signature': f"{'A' * 64}",
                    'slot': 200000000 + i,
                    'timestamp': int(time.time()) - 86400 * i,
                    'from': address,
                    'to': f"{'B' * 44}",
                    'amount': "1000000000",  # 1 SOL
                    'fee': "5000",
                    'status': "confirmed"
                })
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting Solana transaction history for {address}: {e}")
            return []
    
    async def get_credit_score_factors(self, address: str) -> Dict[str, Any]:
        """Get Solana credit score factors"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Mock credit score calculation
            # In production, this would use ML models trained on Solana data
            base_score = 600
            
            # Mock factors based on typical Solana wallet characteristics
            factors = {
                "Account Age": 25,
                "Tx Activity": 45,
                "Balances": 30,
                "DeFi Extras": 40,
                "Staking": 25,
                "Governance": 20,
            }
            
            return {
                'score': base_score,
                'risk': 'Medium Risk',
                'confidence': 0.75,
                'factors': factors,
                'staking_metrics': {
                    'total_staked': 15.0,
                    'staking_duration_days': 120,
                    'is_active_staker': True,
                },
                'governance_metrics': {
                    'total_votes_cast': 12,
                    'participation_rate': 0.7,
                    'is_active_voter': True,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting Solana credit score factors for {address}: {e}")
            return {
                'score': 500,
                'risk': 'Medium Risk',
                'confidence': 0.5,
                'factors': {},
                'staking_metrics': {},
                'governance_metrics': {}
            }


# Register the Solana adapter with the factory
from .base import ChainAdapterFactory
ChainAdapterFactory.register_adapter(ChainType.SOLANA, SolanaAdapter)
