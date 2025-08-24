"""
ML Serving Module for DeFi Credit Scoring
Loads trained models and provides prediction services
"""

import os
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import joblib
import boto3

from features import FeatureExtractor, WalletFeatures

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Result of a credit score prediction"""
    score: float
    confidence: float
    risk_tier: str
    feature_importance: Dict[str, float]
    model_version: str
    prediction_time: float

class CreditScorePredictor:
    """ML model predictor for credit scoring"""
    
    def __init__(self, s3_bucket: str = None, s3_key: str = None):
        self.s3_bucket = s3_bucket or os.getenv("MODEL_S3_BUCKET", "")
        self.s3_key = s3_key or os.getenv("MODEL_S3_KEY", "models/credit_scorer.joblib")
        self.feature_extractor = FeatureExtractor()
        
        # Model state
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_version = None
        self.feature_importance = None
        self.training_metrics = None
        self.model_loaded_at = None
        
        # Load model on initialization
        self.load_model()
    
    def load_model(self, version: str = None) -> bool:
        """
        Load trained model from S3 or local storage
        
        Args:
            version: Model version to load (if None, loads latest)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.s3_bucket:
                model_data = self._load_model_from_s3(version)
            else:
                model_data = self._load_model_local(version)
            
            if model_data is None:
                logger.error("Failed to load model")
                return False
            
            # Extract model components
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_version = model_data.get('version', 'unknown')
            self.feature_importance = model_data.get('feature_importance', {})
            self.training_metrics = model_data.get('training_metrics', {})
            self.model_loaded_at = time.time()
            
            logger.info(f"Model loaded successfully: {self.model_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def _load_model_from_s3(self, version: str = None) -> Optional[Dict[str, Any]]:
        """Load model from S3"""
        try:
            s3_client = boto3.client('s3')
            
            # List objects to find latest version if not specified
            if not version:
                response = s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix=self.s3_key.replace('.joblib', '')
                )
                if 'Contents' in response:
                    latest_key = max(response['Contents'], key=lambda x: x['LastModified'])
                    version = latest_key['Key'].split('_')[-1].replace('.joblib', '')
                else:
                    logger.error("No models found in S3")
                    return None
            
            s3_key = f"{self.s3_key.replace('.joblib', '')}_{version}.joblib"
            
            # Download model
            temp_file = f"/tmp/credit_model_{version}.joblib"
            s3_client.download_file(self.s3_bucket, s3_key, temp_file)
            
            # Load model
            model_data = joblib.load(temp_file)
            
            # Clean up
            os.remove(temp_file)
            
            logger.info(f"Model loaded from S3: s3://{self.s3_bucket}/{s3_key}")
            return model_data
            
        except Exception as e:
            logger.error(f"Error loading model from S3: {e}")
            return None
    
    def _load_model_local(self, version: str = None) -> Optional[Dict[str, Any]]:
        """Load model from local storage"""
        try:
            if version:
                filename = f"models/credit_model_{version}.joblib"
            else:
                # Find latest model
                import glob
                model_files = glob.glob("models/credit_model_*.joblib")
                if not model_files:
                    logger.error("No local models found")
                    return None
                filename = max(model_files, key=os.path.getctime)
            
            model_data = joblib.load(filename)
            logger.info(f"Model loaded locally: {filename}")
            return model_data
            
        except Exception as e:
            logger.error(f"Error loading model locally: {e}")
            return None
    
    def predict(self, wallet_data: Dict[str, Any]) -> PredictionResult:
        """
        Predict credit score for a wallet
        
        Args:
            wallet_data: Dictionary containing wallet information
            
        Returns:
            PredictionResult with score, confidence, and explainability
        """
        start_time = time.time()
        
        try:
            # Check if model is loaded
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Extract features
            features = self.feature_extractor.extract_features(wallet_data)
            feature_dict = self.feature_extractor.features_to_dict(features)
            
            # Convert to DataFrame
            feature_df = pd.DataFrame([feature_dict])
            
            # Ensure all required features are present
            for feature in self.feature_names:
                if feature not in feature_df.columns:
                    feature_df[feature] = 0.0
            
            # Select only the features used by the model
            X = feature_df[self.feature_names]
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            score = self.model.predict(X_scaled)[0]
            
            # Calculate confidence
            confidence = self._calculate_confidence(features, score)
            
            # Determine risk tier
            risk_tier = self._determine_risk_tier(score)
            
            # Calculate feature importance for this prediction
            feature_importance = self._calculate_feature_importance(X_scaled[0])
            
            # Calculate prediction time
            prediction_time = time.time() - start_time
            
            return PredictionResult(
                score=float(score),
                confidence=confidence,
                risk_tier=risk_tier,
                feature_importance=feature_importance,
                model_version=self.model_version,
                prediction_time=prediction_time
            )
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            # Return default prediction
            return PredictionResult(
                score=500.0,
                confidence=0.5,
                risk_tier="Medium Risk",
                feature_importance={},
                model_version=self.model_version or "unknown",
                prediction_time=time.time() - start_time
            )
    
    def _calculate_confidence(self, features: WalletFeatures, score: float) -> float:
        """
        Calculate confidence score for the prediction
        
        Args:
            features: Extracted wallet features
            score: Predicted credit score
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            confidence = 0.7  # Base confidence
            
            # Factor 1: Data completeness
            if features.total_transactions > 0:
                confidence += 0.1
            if features.account_age_days > 0:
                confidence += 0.1
            if features.unique_addresses > 0:
                confidence += 0.05
            
            # Factor 2: Account age (older accounts have more reliable data)
            if features.account_age_days > 365:
                confidence += 0.1
            elif features.account_age_days > 90:
                confidence += 0.05
            
            # Factor 3: Transaction volume (more data = higher confidence)
            if features.total_transactions > 100:
                confidence += 0.05
            
            # Factor 4: Score extremity (extreme scores may be less reliable)
            if 400 <= score <= 800:
                confidence += 0.05
            elif score < 300 or score > 850:
                confidence -= 0.1
            
            # Factor 5: Feature quality
            if features.portfolio_diversity > 0:
                confidence += 0.05
            if features.staking_score > 0:
                confidence += 0.05
            if features.governance_participation > 0:
                confidence += 0.05
            
            return max(0.1, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _determine_risk_tier(self, score: float) -> str:
        """
        Determine risk tier based on credit score
        
        Args:
            score: Credit score
            
        Returns:
            Risk tier string
        """
        if score >= 850:
            return "Very Low Risk"
        elif score >= 700:
            return "Low Risk"
        elif score >= 500:
            return "Medium Risk"
        elif score >= 300:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _calculate_feature_importance(self, scaled_features: np.ndarray) -> Dict[str, float]:
        """
        Calculate feature importance for the current prediction
        
        Args:
            scaled_features: Scaled feature values
            
        Returns:
            Dictionary of feature importance scores
        """
        try:
            if not self.feature_importance:
                return {}
            
            # Use the global feature importance as base
            importance = self.feature_importance.copy()
            
            # Adjust importance based on feature values (higher values = higher importance)
            for i, feature_name in enumerate(self.feature_names):
                if feature_name in importance:
                    # Scale importance by feature value (normalized)
                    feature_value = abs(scaled_features[i])
                    importance[feature_name] *= (1 + feature_value)
            
            # Normalize importance scores
            total_importance = sum(importance.values())
            if total_importance > 0:
                importance = {k: v / total_importance for k, v in importance.items()}
            
            return importance
            
        except Exception as e:
            logger.error(f"Error calculating feature importance: {e}")
            return {}
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        return {
            'version': self.model_version,
            'loaded_at': self.model_loaded_at,
            'feature_names': self.feature_names,
            'training_metrics': self.training_metrics,
            'feature_importance': self.feature_importance,
            'model_type': type(self.model).__name__ if self.model else None,
        }
    
    def is_ready(self) -> bool:
        """Check if the model is ready for predictions"""
        return (
            self.model is not None and
            self.scaler is not None and
            self.feature_names is not None
        )
    
    def reload_model(self, version: str = None) -> bool:
        """
        Reload the model (useful for model updates)
        
        Args:
            version: Model version to load
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("Reloading model")
        return self.load_model(version)


class ModelManager:
    """Manager for multiple model instances"""
    
    def __init__(self):
        self.predictors = {}
        self.default_predictor = None
    
    def add_predictor(self, name: str, predictor: CreditScorePredictor) -> None:
        """Add a predictor to the manager"""
        self.predictors[name] = predictor
        if self.default_predictor is None:
            self.default_predictor = predictor
    
    def get_predictor(self, name: str = None) -> Optional[CreditScorePredictor]:
        """Get a predictor by name or return default"""
        if name is None:
            return self.default_predictor
        return self.predictors.get(name)
    
    def predict(self, wallet_data: Dict[str, Any], model_name: str = None) -> Optional[PredictionResult]:
        """Make prediction using specified or default model"""
        predictor = self.get_predictor(model_name)
        if predictor is None:
            logger.error(f"Predictor not found: {model_name}")
            return None
        
        return predictor.predict(wallet_data)
    
    def get_all_model_info(self) -> Dict[str, Any]:
        """Get information about all models"""
        info = {}
        for name, predictor in self.predictors.items():
            info[name] = {
                'ready': predictor.is_ready(),
                'info': predictor.get_model_info() if predictor.is_ready() else None
            }
        return info


# Global model manager instance
model_manager = ModelManager()


def initialize_models():
    """Initialize all models for the application"""
    try:
        # Initialize default predictor
        default_predictor = CreditScorePredictor()
        model_manager.add_predictor("default", default_predictor)
        
        logger.info("Models initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing models: {e}")
        return False


def predict_credit_score(wallet_data: Dict[str, Any], model_name: str = None) -> Optional[PredictionResult]:
    """
    Convenience function to predict credit score
    
    Args:
        wallet_data: Wallet data dictionary
        model_name: Name of model to use (optional)
        
    Returns:
        PredictionResult or None if failed
    """
    return model_manager.predict(wallet_data, model_name)


def get_model_status() -> Dict[str, Any]:
    """Get status of all models"""
    return model_manager.get_all_model_info()


if __name__ == "__main__":
    # Test the predictor
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize models
    if initialize_models():
        # Test prediction
        test_data = {
            'transactions': [],
            'portfolio': {'tokens': []},
            'protocols': [],
            'staking': {'score': 50},
            'governance': {'participation_rate': 0.5},
            'transaction_count': 100,
            'unique_addresses': 20,
            'first_tx_timestamp': time.time() - 86400 * 30,  # 30 days ago
        }
        
        result = predict_credit_score(test_data)
        if result:
            print(f"Predicted score: {result.score}")
            print(f"Confidence: {result.confidence}")
            print(f"Risk tier: {result.risk_tier}")
            print(f"Model version: {result.model_version}")
        else:
            print("Prediction failed")
    else:
        print("Model initialization failed")
