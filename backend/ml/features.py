"""
Feature Engineering for DeFi Credit Scoring
Extracts model-ready features from wallet data
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class WalletFeatures:
    """Model-ready features for a wallet"""
    # Transaction patterns
    tx_velocity: float  # Transactions per day
    tx_burstiness: float  # Coefficient of variation of inter-arrival times
    tx_periodicity: float  # Regularity of transaction timing
    tx_inter_arrival_variance: float  # Variance of time between transactions
    
    # Portfolio diversity
    portfolio_diversity: float  # Herfindahl index of token holdings
    bluechip_ratio: float  # Ratio of blue-chip tokens
    stable_ratio: float  # Ratio of stablecoins
    volatile_ratio: float  # Ratio of volatile tokens
    
    # Protocol interactions
    protocol_diversity: float  # Number of unique protocols interacted with
    lending_borrowing_ratio: float  # Ratio of lending to borrowing activity
    dex_lp_ratio: float  # Ratio of DEX liquidity provision
    bridge_usage: float  # Cross-chain bridge usage frequency
    
    # Behavioral risk
    risk_address_proximity: float  # Proximity to known risk addresses
    mixer_usage: float  # Usage of privacy mixers
    sanctioned_entity_proximity: float  # Proximity to sanctioned entities
    
    # Staking and governance
    staking_score: float  # Normalized staking activity score
    governance_participation: float  # Governance participation rate
    
    # Account characteristics
    account_age_days: float  # Account age in days
    total_transactions: int  # Total transaction count
    unique_addresses: int  # Number of unique addresses interacted with

class FeatureExtractor:
    """Extract model-ready features from wallet data"""
    
    def __init__(self):
        # Define blue-chip tokens (major cryptocurrencies)
        self.bluechip_tokens = {
            '0xa0b86a33e6441b8c4c8c0b8c4c8c0b8c4c8c0b8c4',  # BTC
            '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',  # WBTC
            '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',  # WETH
            '0x6b175474e89094c44da98b954eedeac495271d0f',  # DAI
            '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  # USDC
            '0xdac17f958d2ee523a2206206994597c13d831ec7',  # USDT
        }
        
        # Define stablecoins
        self.stablecoins = {
            '0x6b175474e89094c44da98b954eedeac495271d0f',  # DAI
            '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  # USDC
            '0xdac17f958d2ee523a2206206994597c13d831ec7',  # USDT
            '0x4fabb145d64652a948d72533023f6e7a623c7c53',  # BUSD
        }
        
        # Known risk addresses (placeholder - would be populated from risk databases)
        self.risk_addresses = set()
        
        # Known mixer addresses (placeholder)
        self.mixer_addresses = set()
        
        # Sanctioned entities (placeholder)
        self.sanctioned_entities = set()
    
    def extract_features(self, wallet_data: Dict[str, Any]) -> WalletFeatures:
        """
        Extract all features from wallet data
        
        Args:
            wallet_data: Dictionary containing wallet information
            
        Returns:
            WalletFeatures object with all extracted features
        """
        try:
            # Extract transaction patterns
            tx_features = self._extract_transaction_patterns(wallet_data.get('transactions', []))
            
            # Extract portfolio features
            portfolio_features = self._extract_portfolio_features(wallet_data.get('portfolio', {}))
            
            # Extract protocol interaction features
            protocol_features = self._extract_protocol_features(wallet_data.get('protocols', []))
            
            # Extract behavioral risk features
            risk_features = self._extract_risk_features(wallet_data.get('transactions', []))
            
            # Extract staking and governance features
            staking_features = self._extract_staking_features(wallet_data.get('staking', {}))
            governance_features = self._extract_governance_features(wallet_data.get('governance', {}))
            
            # Extract account characteristics
            account_features = self._extract_account_features(wallet_data)
            
            return WalletFeatures(
                # Transaction patterns
                tx_velocity=tx_features['velocity'],
                tx_burstiness=tx_features['burstiness'],
                tx_periodicity=tx_features['periodicity'],
                tx_inter_arrival_variance=tx_features['inter_arrival_variance'],
                
                # Portfolio diversity
                portfolio_diversity=portfolio_features['diversity'],
                bluechip_ratio=portfolio_features['bluechip_ratio'],
                stable_ratio=portfolio_features['stable_ratio'],
                volatile_ratio=portfolio_features['volatile_ratio'],
                
                # Protocol interactions
                protocol_diversity=protocol_features['diversity'],
                lending_borrowing_ratio=protocol_features['lending_borrowing_ratio'],
                dex_lp_ratio=protocol_features['dex_lp_ratio'],
                bridge_usage=protocol_features['bridge_usage'],
                
                # Behavioral risk
                risk_address_proximity=risk_features['risk_address_proximity'],
                mixer_usage=risk_features['mixer_usage'],
                sanctioned_entity_proximity=risk_features['sanctioned_entity_proximity'],
                
                # Staking and governance
                staking_score=staking_features['score'],
                governance_participation=governance_features['participation'],
                
                # Account characteristics
                account_age_days=account_features['age_days'],
                total_transactions=account_features['total_transactions'],
                unique_addresses=account_features['unique_addresses'],
            )
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return self._get_default_features()
    
    def _extract_transaction_patterns(self, transactions: List[Dict]) -> Dict[str, float]:
        """Extract transaction pattern features"""
        if not transactions:
            return {
                'velocity': 0.0,
                'burstiness': 0.0,
                'periodicity': 0.0,
                'inter_arrival_variance': 0.0,
            }
        
        try:
            # Sort transactions by timestamp
            sorted_txs = sorted(transactions, key=lambda x: x.get('timestamp', 0))
            
            # Calculate transaction velocity (transactions per day)
            if len(sorted_txs) > 1:
                time_span = sorted_txs[-1]['timestamp'] - sorted_txs[0]['timestamp']
                days_span = max(1, time_span / (24 * 3600))
                velocity = len(sorted_txs) / days_span
            else:
                velocity = 0.0
            
            # Calculate inter-arrival times
            inter_arrival_times = []
            for i in range(1, len(sorted_txs)):
                interval = sorted_txs[i]['timestamp'] - sorted_txs[i-1]['timestamp']
                if interval > 0:
                    inter_arrival_times.append(interval)
            
            if inter_arrival_times:
                # Calculate burstiness (coefficient of variation)
                mean_interval = np.mean(inter_arrival_times)
                std_interval = np.std(inter_arrival_times)
                burstiness = (std_interval - mean_interval) / (std_interval + mean_interval) if (std_interval + mean_interval) > 0 else 0.0
                
                # Calculate inter-arrival variance
                inter_arrival_variance = np.var(inter_arrival_times)
                
                # Calculate periodicity (regularity of timing)
                # Use autocorrelation of inter-arrival times
                if len(inter_arrival_times) > 1:
                    autocorr = np.corrcoef(inter_arrival_times[:-1], inter_arrival_times[1:])[0, 1]
                    periodicity = max(0, autocorr) if not np.isnan(autocorr) else 0.0
                else:
                    periodicity = 0.0
            else:
                burstiness = 0.0
                inter_arrival_variance = 0.0
                periodicity = 0.0
            
            return {
                'velocity': velocity,
                'burstiness': burstiness,
                'periodicity': periodicity,
                'inter_arrival_variance': inter_arrival_variance,
            }
            
        except Exception as e:
            logger.error(f"Error extracting transaction patterns: {e}")
            return {
                'velocity': 0.0,
                'burstiness': 0.0,
                'periodicity': 0.0,
                'inter_arrival_variance': 0.0,
            }
    
    def _extract_portfolio_features(self, portfolio: Dict) -> Dict[str, float]:
        """Extract portfolio diversity features"""
        try:
            if not portfolio or 'tokens' not in portfolio:
                return {
                    'diversity': 0.0,
                    'bluechip_ratio': 0.0,
                    'stable_ratio': 0.0,
                    'volatile_ratio': 0.0,
                }
            
            tokens = portfolio['tokens']
            if not tokens:
                return {
                    'diversity': 0.0,
                    'bluechip_ratio': 0.0,
                    'stable_ratio': 0.0,
                    'volatile_ratio': 0.0,
                }
            
            # Calculate total value
            total_value = sum(token.get('value_usd', 0) for token in tokens)
            if total_value == 0:
                return {
                    'diversity': 0.0,
                    'bluechip_ratio': 0.0,
                    'stable_ratio': 0.0,
                    'volatile_ratio': 0.0,
                }
            
            # Calculate Herfindahl index for diversity
            proportions = [token.get('value_usd', 0) / total_value for token in tokens]
            diversity = 1 - sum(p**2 for p in proportions)  # Inverse Herfindahl
            
            # Calculate token type ratios
            bluechip_value = 0
            stable_value = 0
            volatile_value = 0
            
            for token in tokens:
                token_address = token.get('address', '').lower()
                value = token.get('value_usd', 0)
                
                if token_address in self.bluechip_tokens:
                    bluechip_value += value
                elif token_address in self.stablecoins:
                    stable_value += value
                else:
                    volatile_value += value
            
            bluechip_ratio = bluechip_value / total_value
            stable_ratio = stable_value / total_value
            volatile_ratio = volatile_value / total_value
            
            return {
                'diversity': diversity,
                'bluechip_ratio': bluechip_ratio,
                'stable_ratio': stable_ratio,
                'volatile_ratio': volatile_ratio,
            }
            
        except Exception as e:
            logger.error(f"Error extracting portfolio features: {e}")
            return {
                'diversity': 0.0,
                'bluechip_ratio': 0.0,
                'stable_ratio': 0.0,
                'volatile_ratio': 0.0,
            }
    
    def _extract_protocol_features(self, protocols: List[Dict]) -> Dict[str, float]:
        """Extract protocol interaction features"""
        try:
            if not protocols:
                return {
                    'diversity': 0.0,
                    'lending_borrowing_ratio': 0.0,
                    'dex_lp_ratio': 0.0,
                    'bridge_usage': 0.0,
                }
            
            # Protocol diversity (number of unique protocols)
            unique_protocols = len(set(protocol.get('name', '') for protocol in protocols))
            diversity = min(1.0, unique_protocols / 10)  # Normalize to 0-1
            
            # Calculate activity ratios
            lending_volume = 0
            borrowing_volume = 0
            dex_lp_volume = 0
            bridge_volume = 0
            total_volume = 0
            
            for protocol in protocols:
                volume = protocol.get('volume_usd', 0)
                protocol_type = protocol.get('type', '').lower()
                
                if 'lending' in protocol_type:
                    lending_volume += volume
                elif 'borrowing' in protocol_type:
                    borrowing_volume += volume
                elif 'dex' in protocol_type or 'amm' in protocol_type:
                    dex_lp_volume += volume
                elif 'bridge' in protocol_type:
                    bridge_volume += volume
                
                total_volume += volume
            
            # Calculate ratios
            if total_volume > 0:
                lending_borrowing_ratio = lending_volume / (borrowing_volume + 1)  # Add 1 to avoid division by zero
                dex_lp_ratio = dex_lp_volume / total_volume
                bridge_usage = bridge_volume / total_volume
            else:
                lending_borrowing_ratio = 0.0
                dex_lp_ratio = 0.0
                bridge_usage = 0.0
            
            return {
                'diversity': diversity,
                'lending_borrowing_ratio': lending_borrowing_ratio,
                'dex_lp_ratio': dex_lp_ratio,
                'bridge_usage': bridge_usage,
            }
            
        except Exception as e:
            logger.error(f"Error extracting protocol features: {e}")
            return {
                'diversity': 0.0,
                'lending_borrowing_ratio': 0.0,
                'dex_lp_ratio': 0.0,
                'bridge_usage': 0.0,
            }
    
    def _extract_risk_features(self, transactions: List[Dict]) -> Dict[str, float]:
        """Extract behavioral risk features"""
        try:
            if not transactions:
                return {
                    'risk_address_proximity': 0.0,
                    'mixer_usage': 0.0,
                    'sanctioned_entity_proximity': 0.0,
                }
            
            risk_interactions = 0
            mixer_interactions = 0
            sanctioned_interactions = 0
            total_interactions = len(transactions)
            
            for tx in transactions:
                # Check if transaction involves risk addresses
                to_address = tx.get('to', '').lower()
                from_address = tx.get('from', '').lower()
                
                if to_address in self.risk_addresses or from_address in self.risk_addresses:
                    risk_interactions += 1
                
                if to_address in self.mixer_addresses or from_address in self.mixer_addresses:
                    mixer_interactions += 1
                
                if to_address in self.sanctioned_entities or from_address in self.sanctioned_entities:
                    sanctioned_interactions += 1
            
            # Calculate ratios
            risk_address_proximity = risk_interactions / total_interactions if total_interactions > 0 else 0.0
            mixer_usage = mixer_interactions / total_interactions if total_interactions > 0 else 0.0
            sanctioned_entity_proximity = sanctioned_interactions / total_interactions if total_interactions > 0 else 0.0
            
            return {
                'risk_address_proximity': risk_address_proximity,
                'mixer_usage': mixer_usage,
                'sanctioned_entity_proximity': sanctioned_entity_proximity,
            }
            
        except Exception as e:
            logger.error(f"Error extracting risk features: {e}")
            return {
                'risk_address_proximity': 0.0,
                'mixer_usage': 0.0,
                'sanctioned_entity_proximity': 0.0,
            }
    
    def _extract_staking_features(self, staking_data: Dict) -> Dict[str, float]:
        """Extract staking features"""
        try:
            if not staking_data:
                return {'score': 0.0}
            
            # Normalize staking score to 0-1 range
            staking_score = staking_data.get('score', 0)
            normalized_score = max(0, min(1, (staking_score + 50) / 150))  # Assuming score range -50 to 100
            
            return {'score': normalized_score}
            
        except Exception as e:
            logger.error(f"Error extracting staking features: {e}")
            return {'score': 0.0}
    
    def _extract_governance_features(self, governance_data: Dict) -> Dict[str, float]:
        """Extract governance features"""
        try:
            if not governance_data:
                return {'participation': 0.0}
            
            # Use participation rate directly
            participation = governance_data.get('participation_rate', 0.0)
            
            return {'participation': participation}
            
        except Exception as e:
            logger.error(f"Error extracting governance features: {e}")
            return {'participation': 0.0}
    
    def _extract_account_features(self, wallet_data: Dict) -> Dict[str, Any]:
        """Extract account characteristic features"""
        try:
            # Account age
            first_tx_timestamp = wallet_data.get('first_tx_timestamp')
            if first_tx_timestamp:
                age_seconds = time.time() - first_tx_timestamp
                age_days = age_seconds / (24 * 3600)
            else:
                age_days = 0.0
            
            # Transaction count
            total_transactions = wallet_data.get('transaction_count', 0)
            
            # Unique addresses
            unique_addresses = wallet_data.get('unique_addresses', 0)
            
            return {
                'age_days': age_days,
                'total_transactions': total_transactions,
                'unique_addresses': unique_addresses,
            }
            
        except Exception as e:
            logger.error(f"Error extracting account features: {e}")
            return {
                'age_days': 0.0,
                'total_transactions': 0,
                'unique_addresses': 0,
            }
    
    def _get_default_features(self) -> WalletFeatures:
        """Return default features when extraction fails"""
        return WalletFeatures(
            tx_velocity=0.0,
            tx_burstiness=0.0,
            tx_periodicity=0.0,
            tx_inter_arrival_variance=0.0,
            portfolio_diversity=0.0,
            bluechip_ratio=0.0,
            stable_ratio=0.0,
            volatile_ratio=0.0,
            protocol_diversity=0.0,
            lending_borrowing_ratio=0.0,
            dex_lp_ratio=0.0,
            bridge_usage=0.0,
            risk_address_proximity=0.0,
            mixer_usage=0.0,
            sanctioned_entity_proximity=0.0,
            staking_score=0.0,
            governance_participation=0.0,
            account_age_days=0.0,
            total_transactions=0,
            unique_addresses=0,
        )
    
    def features_to_dict(self, features: WalletFeatures) -> Dict[str, float]:
        """Convert WalletFeatures to dictionary for model input"""
        return {
            'tx_velocity': features.tx_velocity,
            'tx_burstiness': features.tx_burstiness,
            'tx_periodicity': features.tx_periodicity,
            'tx_inter_arrival_variance': features.tx_inter_arrival_variance,
            'portfolio_diversity': features.portfolio_diversity,
            'bluechip_ratio': features.bluechip_ratio,
            'stable_ratio': features.stable_ratio,
            'volatile_ratio': features.volatile_ratio,
            'protocol_diversity': features.protocol_diversity,
            'lending_borrowing_ratio': features.lending_borrowing_ratio,
            'dex_lp_ratio': features.dex_lp_ratio,
            'bridge_usage': features.bridge_usage,
            'risk_address_proximity': features.risk_address_proximity,
            'mixer_usage': features.mixer_usage,
            'sanctioned_entity_proximity': features.sanctioned_entity_proximity,
            'staking_score': features.staking_score,
            'governance_participation': features.governance_participation,
            'account_age_days': features.account_age_days,
            'total_transactions': features.total_transactions,
            'unique_addresses': features.unique_addresses,
        }
