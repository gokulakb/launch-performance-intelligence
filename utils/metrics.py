"""
Metric calculation utilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class MetricsCalculator:
    """Utility class for calculating various metrics."""
    
    @staticmethod
    def calculate_growth_rate(values: List[float], period: int = 1) -> float:
        """
        Calculate growth rate over a period.
        
        Args:
            values: List of values
            period: Number of periods to look back
        
        Returns:
            Growth rate as percentage
        """
        if len(values) < period + 1:
            return 0
        
        current = values[-1]
        previous = values[-period - 1]
        
        if previous == 0:
            return 0
        
        return ((current - previous) / previous) * 100
    
    @staticmethod
    def calculate_cagr(start_value: float, end_value: float, periods: int) -> float:
        """
        Calculate Compound Annual Growth Rate.
        
        Args:
            start_value: Starting value
            end_value: Ending value
            periods: Number of periods
        
        Returns:
            CAGR as percentage
        """
        if start_value == 0 or periods == 0:
            return 0
        
        return ((end_value / start_value) ** (1 / periods) - 1) * 100
    
    @staticmethod
    def calculate_moving_average(values: List[float], window: int = 7) -> List[float]:
        """
        Calculate moving average.
        
        Args:
            values: List of values
            window: Window size
        
        Returns:
            List of moving averages
        """
        if len(values) < window:
            return []
        
        ma = []
        for i in range(window - 1, len(values)):
            avg = sum(values[i - window + 1:i + 1]) / window
            ma.append(avg)
        
        return ma
    
    @staticmethod
    def calculate_volatility(values: List[float]) -> float:
        """
        Calculate volatility (standard deviation of returns).
        
        Args:
            values: List of values
        
        Returns:
            Volatility as percentage
        """
        if len(values) < 2:
            return 0
        
        returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values)) if values[i-1] != 0]
        
        if not returns:
            return 0
        
        return np.std(returns) * 100
    
    @staticmethod
    def calculate_percentiles(values: List[float], percentiles: List[int] = [25, 50, 75]) -> Dict[int, float]:
        """
        Calculate percentiles.
        
        Args:
            values: List of values
            percentiles: List of percentile values
        
        Returns:
            Dictionary of percentile values
        """
        if not values:
            return {p: 0 for p in percentiles}
        
        result = {}
        for p in percentiles:
            result[p] = np.percentile(values, p)
        
        return result
    
    @staticmethod
    def calculate_confidence_interval(values: List[float], confidence: float = 0.95) -> Dict[str, float]:
        """
        Calculate confidence interval.
        
        Args:
            values: List of values
            confidence: Confidence level
        
        Returns:
            Dictionary with confidence interval
        """
        if len(values) < 2:
            return {'lower': 0, 'upper': 0, 'mean': 0}
        
        mean = np.mean(values)
        std = np.std(values)
        n = len(values)
        
        # Z-score for confidence level
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z = z_scores.get(confidence, 1.96)
        
        margin = z * (std / np.sqrt(n))
        
        return {
            'lower': mean - margin,
            'upper': mean + margin,
            'mean': mean
        }
    
    @staticmethod
    def calculate_churn_metrics(active_users: List[int], churned_users: List[int]) -> Dict[str, float]:
        """
        Calculate churn metrics.
        
        Args:
            active_users: List of active user counts
            churned_users: List of churned user counts
        
        Returns:
            Dictionary with churn metrics
        """
        if not active_users or not churned_users:
            return {'churn_rate': 0, 'net_churn': 0, 'gross_churn': 0}
        
        # Calculate churn rate
        total_active = sum(active_users)
        total_churned = sum(churned_users)
        
        churn_rate = (total_churned / total_active) * 100 if total_active > 0 else 0
        
        # Calculate net churn (if we have consecutive periods)
        net_churn = 0
        if len(active_users) > 1:
            net_change = active_users[-1] - active_users[0]
            net_churn = (net_change / active_users[0]) * 100 if active_users[0] > 0 else 0
        
        return {
            'churn_rate': churn_rate,
            'net_churn': net_churn,
            'gross_churn': churn_rate
        }
    
    @staticmethod
    def calculate_retention_metrics(cohort_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate retention metrics from cohort data.
        
        Args:
            cohort_data: DataFrame with cohort retention data
        
        Returns:
            Dictionary with retention metrics
        """
        if cohort_data.empty:
            return {'day_1': 0, 'day_7': 0, 'day_30': 0, 'monthly': 0}
        
        metrics = {}
        
        # Calculate average retention for each period
        for period in ['day_1_retained', 'day_7_retained', 'day_30_retained', 'monthly_retained']:
            if period in cohort_data.columns:
                metrics[period.replace('_retained', '')] = cohort_data[period].mean() * 100
        
        return metrics
    
    @staticmethod
    def calculate_engagement_score(metrics: Dict[str, float]) -> float:
        """
        Calculate engagement score from multiple metrics.
        
        Args:
            metrics: Dictionary of metrics
        
        Returns:
            Engagement score (0-100)
        """
        weights = {
            'active_users': 0.3,
            'retention_d1': 0.2,
            'retention_d7': 0.15,
            'retention_d30': 0.15,
            'sessions_per_user': 0.1,
            'time_spent': 0.1
        }
        
        score = 0
        for metric, weight in weights.items():
            value = metrics.get(metric, 0)
            # Normalize value if needed
            if metric == 'retention_d1' or metric == 'retention_d7' or metric == 'retention_d30':
                value = min(value, 100)
            elif metric == 'active_users':
                value = min(value / 1000, 100)  # Normalize to 100 for 1000 users
            elif metric == 'sessions_per_user':
                value = min(value * 10, 100)  # Normalize to 100 for 10 sessions
            elif metric == 'time_spent':
                value = min(value / 60, 100)  # Normalize to 100 for 60 minutes
            
            score += value * weight
        
        return min(score, 100)