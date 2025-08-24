"""
ML Training Script for DeFi Credit Scoring
Trains models using extracted features and saves to S3
"""

import os
import json
import time
import boto3
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import lightgbm as lgb
import logging
from datetime import datetime

from features import FeatureExtractor, WalletFeatures

logger = logging.getLogger(__name__)

class CreditScoreTrainer:
    """Trainer for DeFi credit scoring models"""
    
    def __init__(self, s3_bucket: str = None, s3_key: str = None):
        self.s3_bucket = s3_bucket or os.getenv("MODEL_S3_BUCKET", "")
        self.s3_key = s3_key or os.getenv("MODEL_S3_KEY", "models/credit_scorer.joblib")
        self.feature_extractor = FeatureExtractor()
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
    def generate_synthetic_data(self, num_samples: int = 10000) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Generate synthetic training data for demonstration
        
        In production, this would be replaced with real historical data
        """
        logger.info(f"Generating {num_samples} synthetic training samples")
        
        np.random.seed(42)
        
        # Generate synthetic features
        data = {
            # Transaction patterns
            'tx_velocity': np.random.exponential(5, num_samples),
            'tx_burstiness': np.random.uniform(-0.5, 0.8, num_samples),
            'tx_periodicity': np.random.uniform(0, 0.9, num_samples),
            'tx_inter_arrival_variance': np.random.exponential(1000, num_samples),
            
            # Portfolio diversity
            'portfolio_diversity': np.random.uniform(0, 1, num_samples),
            'bluechip_ratio': np.random.uniform(0, 1, num_samples),
            'stable_ratio': np.random.uniform(0, 1, num_samples),
            'volatile_ratio': np.random.uniform(0, 1, num_samples),
            
            # Protocol interactions
            'protocol_diversity': np.random.uniform(0, 1, num_samples),
            'lending_borrowing_ratio': np.random.exponential(2, num_samples),
            'dex_lp_ratio': np.random.uniform(0, 1, num_samples),
            'bridge_usage': np.random.uniform(0, 0.3, num_samples),
            
            # Behavioral risk
            'risk_address_proximity': np.random.uniform(0, 0.2, num_samples),
            'mixer_usage': np.random.uniform(0, 0.1, num_samples),
            'sanctioned_entity_proximity': np.random.uniform(0, 0.05, num_samples),
            
            # Staking and governance
            'staking_score': np.random.uniform(0, 1, num_samples),
            'governance_participation': np.random.uniform(0, 1, num_samples),
            
            # Account characteristics
            'account_age_days': np.random.exponential(365, num_samples),
            'total_transactions': np.random.poisson(100, num_samples),
            'unique_addresses': np.random.poisson(20, num_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate synthetic credit scores based on features
        # Higher scores for: older accounts, more transactions, higher staking, lower risk
        # Lower scores for: high risk proximity, high mixer usage, low diversity
        base_score = 500
        
        # Positive factors
        age_bonus = np.clip(df['account_age_days'] / 365 * 50, 0, 100)
        tx_bonus = np.clip(df['total_transactions'] / 100 * 30, 0, 100)
        staking_bonus = df['staking_score'] * 50
        governance_bonus = df['governance_participation'] * 30
        diversity_bonus = df['portfolio_diversity'] * 20
        bluechip_bonus = df['bluechip_ratio'] * 15
        
        # Negative factors
        risk_penalty = df['risk_address_proximity'] * -200
        mixer_penalty = df['mixer_usage'] * -300
        sanctioned_penalty = df['sanctioned_entity_proximity'] * -500
        
        # Calculate final scores
        scores = (base_score + age_bonus + tx_bonus + staking_bonus + 
                 governance_bonus + diversity_bonus + bluechip_bonus + 
                 risk_penalty + mixer_penalty + sanctioned_penalty)
        
        # Clip to valid range and add noise
        scores = np.clip(scores, 300, 850)
        scores += np.random.normal(0, 20, num_samples)
        scores = np.clip(scores, 300, 850)
        
        return df, pd.Series(scores)
    
    def train_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Train multiple credit scoring models
        
        Args:
            X: Feature matrix
            y: Target credit scores
            
        Returns:
            Dictionary containing trained models and metrics
        """
        logger.info("Training credit scoring models")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Initialize models
        models = {
            'random_forest': RandomForestRegressor(
                n_estimators=100, 
                max_depth=10, 
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'xgboost': xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            ),
            'lightgbm': lgb.LGBMRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
        }
        
        # Train models and collect metrics
        results = {}
        scalers = {}
        
        for name, model in models.items():
            logger.info(f"Training {name} model")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                importance = dict(zip(X.columns, model.feature_importances_))
            else:
                importance = {}
            
            results[name] = {
                'model': model,
                'metrics': {
                    'mse': mse,
                    'rmse': rmse,
                    'mae': mae,
                    'r2': r2,
                    'cv_r2_mean': cv_scores.mean(),
                    'cv_r2_std': cv_scores.std()
                },
                'feature_importance': importance
            }
            
            logger.info(f"{name} - R²: {r2:.4f}, RMSE: {rmse:.2f}, CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        
        # Select best model based on CV score
        best_model_name = max(results.keys(), key=lambda k: results[k]['metrics']['cv_r2_mean'])
        best_model = results[best_model_name]['model']
        
        logger.info(f"Best model: {best_model_name}")
        
        # Create scaler for the best model
        scaler = StandardScaler()
        scaler.fit(X_train)
        
        return {
            'best_model': best_model,
            'best_model_name': best_model_name,
            'scaler': scaler,
            'all_models': results,
            'feature_names': list(X.columns)
        }
    
    def save_model_to_s3(self, model_data: Dict[str, Any], version: str = None) -> bool:
        """
        Save trained model to S3
        
        Args:
            model_data: Dictionary containing model and metadata
            version: Model version string
            
        Returns:
            True if successful, False otherwise
        """
        if not self.s3_bucket:
            logger.warning("S3 bucket not configured, saving locally")
            return self.save_model_local(model_data, version)
        
        try:
            # Create S3 client
            s3_client = boto3.client('s3')
            
            # Prepare model package
            model_package = {
                'model': model_data['best_model'],
                'scaler': model_data['scaler'],
                'feature_names': model_data['feature_names'],
                'best_model_name': model_data['best_model_name'],
                'training_metrics': model_data['all_models'][model_data['best_model_name']]['metrics'],
                'feature_importance': model_data['all_models'][model_data['best_model_name']]['feature_importance'],
                'version': version or datetime.now().strftime("%Y%m%d_%H%M%S"),
                'created_at': datetime.now().isoformat(),
            }
            
            # Save to temporary file
            temp_file = f"/tmp/credit_model_{version}.joblib"
            joblib.dump(model_package, temp_file)
            
            # Upload to S3
            s3_key = f"{self.s3_key.replace('.joblib', '')}_{version}.joblib"
            s3_client.upload_file(temp_file, self.s3_bucket, s3_key)
            
            # Clean up
            os.remove(temp_file)
            
            logger.info(f"Model saved to S3: s3://{self.s3_bucket}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model to S3: {e}")
            return False
    
    def save_model_local(self, model_data: Dict[str, Any], version: str = None) -> bool:
        """Save model locally as fallback"""
        try:
            model_package = {
                'model': model_data['best_model'],
                'scaler': model_data['scaler'],
                'feature_names': model_data['feature_names'],
                'best_model_name': model_data['best_model_name'],
                'training_metrics': model_data['all_models'][model_data['best_model_name']]['metrics'],
                'feature_importance': model_data['all_models'][model_data['best_model_name']]['feature_importance'],
                'version': version or datetime.now().strftime("%Y%m%d_%H%M%S"),
                'created_at': datetime.now().isoformat(),
            }
            
            filename = f"models/credit_model_{version}.joblib"
            os.makedirs("models", exist_ok=True)
            joblib.dump(model_package, filename)
            
            logger.info(f"Model saved locally: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model locally: {e}")
            return False
    
    def load_model_from_s3(self, version: str = None) -> Optional[Dict[str, Any]]:
        """
        Load trained model from S3
        
        Args:
            version: Model version to load (if None, loads latest)
            
        Returns:
            Model data dictionary or None if failed
        """
        if not self.s3_bucket:
            logger.warning("S3 bucket not configured, loading from local")
            return self.load_model_local(version)
        
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
    
    def load_model_local(self, version: str = None) -> Optional[Dict[str, Any]]:
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
    
    def train_and_save(self, num_samples: int = 10000, version: str = None) -> bool:
        """
        Complete training pipeline: generate data, train models, save to S3
        
        Args:
            num_samples: Number of synthetic samples to generate
            version: Model version string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate training data
            X, y = self.generate_synthetic_data(num_samples)
            
            # Train models
            model_data = self.train_models(X, y)
            
            # Save model
            success = self.save_model_to_s3(model_data, version)
            
            if success:
                logger.info("Training pipeline completed successfully")
                return True
            else:
                logger.error("Failed to save model")
                return False
                
        except Exception as e:
            logger.error(f"Training pipeline failed: {e}")
            return False


def main():
    """Main training script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train DeFi credit scoring models")
    parser.add_argument("--samples", type=int, default=10000, help="Number of training samples")
    parser.add_argument("--version", type=str, help="Model version")
    parser.add_argument("--s3-bucket", type=str, help="S3 bucket for model storage")
    parser.add_argument("--s3-key", type=str, help="S3 key for model storage")
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = CreditScoreTrainer(
        s3_bucket=args.s3_bucket,
        s3_key=args.s3_key
    )
    
    # Run training pipeline
    success = trainer.train_and_save(
        num_samples=args.samples,
        version=args.version
    )
    
    if success:
        print("Training completed successfully!")
    else:
        print("Training failed!")
        exit(1)


if __name__ == "__main__":
    main()
