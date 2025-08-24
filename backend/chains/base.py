"""
Base Chain Adapter Interface
Defines the common interface for all blockchain adapters
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ChainType(Enum):
    """Supported blockchain types"""
    SEI = "sei"
    ETHEREUM = "eth"
    SOLANA = "sol"

@dataclass
class WalletProfile:
    """Standardized wallet profile across all chains"""
    address: str
    chain: ChainType
    balance_native: float
    balance_usd: float
    transaction_count: int
    first_tx_timestamp: Optional[int]
    last_tx_timestamp: Optional[int]
    unique_addresses: int
    is_contract: bool
    risk_score: float
    confidence: float

@dataclass
class StakingMetrics:
    """Standardized staking metrics across all chains"""
    total_staked: float
    staking_duration_days: int
    rewards_earned: float
    penalties_incurred: float
    validator_count: int
    is_active_staker: bool
    staking_score: float

@dataclass
class GovernanceMetrics:
    """Standardized governance metrics across all chains"""
    total_votes_cast: int
    proposals_participated: int
    recent_votes_90d: int
    voting_power_used: float
    participation_rate: float
    is_active_voter: bool
    governance_score: float

@dataclass
class ProtocolInteraction:
    """Standardized protocol interaction data"""
    protocol_name: str
    protocol_type: str  # lending, dex, bridge, etc.
    total_volume_usd: float
    interaction_count: int
    last_interaction_timestamp: Optional[int]
    risk_level: str  # low, medium, high

@dataclass
class TokenBalance:
    """Standardized token balance data"""
    token_address: str
    token_symbol: str
    balance_raw: str
    balance_formatted: float
    value_usd: float
    price_usd: float
    is_stablecoin: bool
    is_bluechip: bool

class ChainAdapter(ABC):
    """
    Abstract base class for blockchain adapters
    
    All chain adapters must implement this interface to ensure
    consistent data structures across different blockchains.
    """
    
    def __init__(self, chain_type: ChainType, rpc_url: str):
        self.chain_type = chain_type
        self.rpc_url = rpc_url
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the blockchain RPC
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """
        Validate wallet address format for this chain
        
        Args:
            address: Wallet address to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_wallet_profile(self, address: str) -> WalletProfile:
        """
        Get comprehensive wallet profile
        
        Args:
            address: Wallet address
            
        Returns:
            WalletProfile object with wallet data
        """
        pass
    
    @abstractmethod
    async def get_staking_metrics(self, address: str) -> StakingMetrics:
        """
        Get staking metrics for wallet
        
        Args:
            address: Wallet address
            
        Returns:
            StakingMetrics object with staking data
        """
        pass
    
    @abstractmethod
    async def get_governance_metrics(self, address: str) -> GovernanceMetrics:
        """
        Get governance metrics for wallet
        
        Args:
            address: Wallet address
            
        Returns:
            GovernanceMetrics object with governance data
        """
        pass
    
    @abstractmethod
    async def get_protocol_interactions(self, address: str) -> List[ProtocolInteraction]:
        """
        Get protocol interaction history
        
        Args:
            address: Wallet address
            
        Returns:
            List of ProtocolInteraction objects
        """
        pass
    
    @abstractmethod
    async def get_token_balances(self, address: str) -> List[TokenBalance]:
        """
        Get token balances for wallet
        
        Args:
            address: Wallet address
            
        Returns:
            List of TokenBalance objects
        """
        pass
    
    @abstractmethod
    async def get_transaction_history(self, address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get transaction history for wallet
        
        Args:
            address: Wallet address
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        pass
    
    @abstractmethod
    async def get_credit_score_factors(self, address: str) -> Dict[str, Any]:
        """
        Get credit score factors for wallet
        
        Args:
            address: Wallet address
            
        Returns:
            Dictionary of credit score factors
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for the adapter
        
        Returns:
            Dictionary with health status information
        """
        return {
            'chain_type': self.chain_type.value,
            'rpc_url': self.rpc_url,
            'is_connected': self.is_connected,
            'status': 'healthy' if self.is_connected else 'disconnected'
        }
    
    def get_chain_type(self) -> ChainType:
        """Get the chain type for this adapter"""
        return self.chain_type
    
    async def disconnect(self) -> None:
        """Disconnect from the blockchain RPC"""
        self.is_connected = False


class ChainAdapterFactory:
    """Factory for creating chain adapters"""
    
    _adapters = {}
    
    @classmethod
    def register_adapter(cls, chain_type: ChainType, adapter_class: type):
        """Register a chain adapter class"""
        cls._adapters[chain_type] = adapter_class
    
    @classmethod
    def create_adapter(cls, chain_type: ChainType, rpc_url: str) -> Optional[ChainAdapter]:
        """
        Create a chain adapter instance
        
        Args:
            chain_type: Type of blockchain
            rpc_url: RPC URL for the blockchain
            
        Returns:
            ChainAdapter instance or None if not supported
        """
        adapter_class = cls._adapters.get(chain_type)
        if adapter_class is None:
            return None
        
        return adapter_class(chain_type, rpc_url)
    
    @classmethod
    def get_supported_chains(cls) -> List[ChainType]:
        """Get list of supported chain types"""
        return list(cls._adapters.keys())


# Convenience functions
def get_chain_adapter(chain_type: str, rpc_url: str) -> Optional[ChainAdapter]:
    """
    Get a chain adapter by type string
    
    Args:
        chain_type: Chain type string ('sei', 'eth', 'sol')
        rpc_url: RPC URL for the blockchain
        
    Returns:
        ChainAdapter instance or None if not supported
    """
    try:
        chain_enum = ChainType(chain_type.lower())
        return ChainAdapterFactory.create_adapter(chain_enum, rpc_url)
    except ValueError:
        return None


def get_supported_chains() -> List[str]:
    """Get list of supported chain types as strings"""
    return [chain.value for chain in ChainAdapterFactory.get_supported_chains()]
