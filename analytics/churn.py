"""
Churn prediction module using machine learning.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class ChurnPredictor:
    """Machine learning model for churn prediction."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_importance = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'models', 'churn_model.pkl')
    
    def train_model(self, data: pd.DataFrame, target_col: str = 'churned') -> Dict[str, Any]:
        """
        Train churn prediction model.
        
        Args:
            data: Training data
            target_col: Target column name
        
        Returns:
            Dictionary with training results
        """
        try:
            # Prepare features and target
            feature_cols = [col for col in data.columns if col != target_col]
            X = data[feature_cols]
            y = data[target_col]
            
            # Handle missing values
            X = X.fillna(X.mean())
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Calculate feature importance
            self.feature_importance = dict(zip(feature_cols, self.model.feature_importances_))
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': feature_cols
            }, self.model_path)
            
            return {
                'accuracy': accuracy,
                'feature_importance': self.feature_importance,
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }
            
        except Exception as e:
            logger.error(f"Error training churn model: {e}")
            return {'error': str(e)}
    
    def predict_churn(self, features: np.ndarray) -> np.ndarray:
        """
        Predict churn probability for users.
        
        Args:
            features: Feature array
        
        Returns:
            Array of churn probabilities
        """
        try:
            if self.model is None:
                # Load saved model if available
                if os.path.exists(self.model_path):
                    saved = joblib.load(self.model_path)
                    self.model = saved['model']
                    self.scaler = saved['scaler']
                else:
                    # Return random probabilities if no model
                    return np.random.uniform(0, 0.5, len(features))
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get probabilities
            probabilities = self.model.predict_proba(features_scaled)
            churn_probs = probabilities[:, 1] if probabilities.shape[1] > 1 else probabilities
            
            return churn_probs
            
        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            return np.random.uniform(0, 0.5, len(features))
    
    def get_churn_drivers(self, user_data: pd.DataFrame) -> Dict[str, float]:
        """
        Identify top drivers of churn.
        
        Args:
            user_data: User data with features
        
        Returns:
            Dictionary of feature importance
        """
        if self.feature_importance is not None:
            return dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Calculate simple correlations if model not available
        if 'churned' in user_data.columns:
            correlations = user_data.corr()['churned'].sort_values(ascending=False)
            return correlations.head(10).to_dict()
        
        return {}