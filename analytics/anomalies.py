"""
Anomaly detection module for identifying unusual patterns.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Anomaly detection in metrics and events."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
    
    def detect_anomalies(self, df: pd.DataFrame, columns: List[str], 
                         contamination: float = 0.1) -> Dict[str, Any]:
        """
        Detect anomalies in data using Isolation Forest.
        
        Args:
            df: DataFrame
            columns: Columns to analyze
            contamination: Expected proportion of anomalies
        
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            if df.empty or not all(col in df.columns for col in columns):
                return {'anomalies': [], 'scores': [], 'indices': []}
            
            # Prepare data
            X = df[columns].fillna(df[columns].mean())
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model = IsolationForest(
                contamination=contamination,
                random_state=42
            )
            predictions = self.model.fit_predict(X_scaled)
            scores = self.model.score_samples(X_scaled)
            
            # Identify anomalies
            anomaly_indices = np.where(predictions == -1)[0].tolist()
            
            return {
                'indices': anomaly_indices,
                'scores': scores.tolist(),
                'predictions': predictions.tolist(),
                'anomaly_count': len(anomaly_indices),
                'anomaly_ratio': len(anomaly_indices) / len(df) if len(df) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {'anomalies': [], 'scores': [], 'indices': []}
    
    def detect_spikes(self, values: List[float], threshold: float = 2.0) -> List[int]:
        """
        Detect spikes in time series data.
        
        Args:
            values: List of values
            threshold: Z-score threshold for spikes
        
        Returns:
            List of spike indices
        """
        try:
            if len(values) < 3:
                return []
            
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                return []
            
            z_scores = [(v - mean) / std for v in values]
            
            # Find positive spikes (increase)
            spikes = [i for i, z in enumerate(z_scores) if z > threshold]
            
            # Only include spikes where previous value wasn't already high
            filtered_spikes = []
            for i in spikes:
                if i > 0 and z_scores[i] > z_scores[i-1] * 1.5:
                    filtered_spikes.append(i)
            
            return filtered_spikes
            
        except Exception as e:
            logger.error(f"Error detecting spikes: {e}")
            return []
    
    def detect_drops(self, values: List[float], threshold: float = 2.0) -> List[int]:
        """
        Detect sudden drops in time series data.
        
        Args:
            values: List of values
            threshold: Z-score threshold for drops
        
        Returns:
            List of drop indices
        """
        try:
            if len(values) < 3:
                return []
            
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                return []
            
            z_scores = [(v - mean) / std for v in values]
            
            # Find negative drops
            drops = [i for i, z in enumerate(z_scores) if z < -threshold]
            
            # Only include drops where previous value wasn't already low
            filtered_drops = []
            for i in drops:
                if i > 0 and z_scores[i] < z_scores[i-1] * 0.5:
                    filtered_drops.append(i)
            
            return filtered_drops
            
        except Exception as e:
            logger.error(f"Error detecting drops: {e}")
            return []
    
    def detect_seasonal_anomalies(self, values: List[float], 
                                  season_length: int = 7) -> List[int]:
        """
        Detect anomalies considering seasonal patterns.
        
        Args:
            values: Time series values
            season_length: Seasonal period (e.g., 7 for weekly)
        
        Returns:
            List of anomaly indices
        """
        try:
            if len(values) < season_length * 2:
                return []
            
            anomalies = []
            
            # Calculate seasonal components
            for i in range(season_length, len(values)):
                # Get same season values from previous periods
                season_values = values[i % season_length::season_length]
                
                if len(season_values) < 3:
                    continue
                
                mean = np.mean(season_values[:-1])  # Exclude current
                std = np.std(season_values[:-1])
                
                if std == 0:
                    continue
                
                z_score = (values[i] - mean) / std
                
                if abs(z_score) > 2.5:
                    anomalies.append(i)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting seasonal anomalies: {e}")
            return []
    
    def detect_pattern_breaks(self, df: pd.DataFrame, column: str) -> List[int]:
        """
        Detect breaks in patterns (change points).
        
        Args:
            df: DataFrame
            column: Column to analyze
        
        Returns:
            List of break point indices
        """
        try:
            if column not in df.columns or len(df) < 10:
                return []
            
            values = df[column].values
            
            breaks = []
            window = 5
            
            for i in range(window, len(values) - window):
                before = values[i - window:i]
                after = values[i + 1:i + window + 1]
                
                if len(before) < 2 or len(after) < 2:
                    continue
                
                # Compare means
                mean_before = np.mean(before)
                mean_after = np.mean(after)
                
                # Compare trends
                trend_before = np.polyfit(range(len(before)), before, 1)[0]
                trend_after = np.polyfit(range(len(after)), after, 1)[0]
                
                # Significant change in mean or trend
                if abs(mean_after - mean_before) > np.std(values) * 0.5:
                    breaks.append(i)
                elif abs(trend_after - trend_before) > 0.1:
                    breaks.append(i)
            
            return breaks
            
        except Exception as e:
            logger.error(f"Error detecting pattern breaks: {e}")
            return []