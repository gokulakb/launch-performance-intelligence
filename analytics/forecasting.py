"""
Forecasting module for revenue and growth predictions.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class RevenueForecaster:
    """Revenue forecasting using machine learning."""
    
    def __init__(self):
        self.model = None
        self.poly = None
    
    def forecast_revenue(self, historical_data: pd.DataFrame, periods: int = 30) -> List[Dict[str, Any]]:
        """
        Forecast revenue for future periods.
        
        Args:
            historical_data: DataFrame with 'date' and 'revenue' columns
            periods: Number of periods to forecast
        
        Returns:
            List of forecasted values
        """
        try:
            if historical_data.empty or len(historical_data) < 7:
                return self._generate_simple_forecast(historical_data, periods)
            
            # Prepare data
            data = historical_data.sort_values('date').copy()
            data['day_index'] = range(len(data))
            data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
            data['month'] = pd.to_datetime(data['date']).dt.month
            
            # Get daily averages for seasonality
            daily_avg = data.groupby('day_of_week')['revenue'].mean().to_dict()
            
            # Train multiple models
            X = data[['day_index', 'day_of_week', 'month']].values
            
            # Polynomial features for trend
            self.poly = PolynomialFeatures(degree=2)
            X_poly = self.poly.fit_transform(X[:, 0].reshape(-1, 1))
            
            # Linear trend model
            trend_model = LinearRegression()
            trend_model.fit(X[:, 0].reshape(-1, 1), data['revenue'].values)
            
            # Generate forecast
            last_day = data['day_index'].max()
            forecast = []
            
            for i in range(1, periods + 1):
                day_idx = last_day + i
                future_date = pd.to_datetime(data['date'].max()) + timedelta(days=i)
                
                # Trend component
                trend_value = trend_model.predict([[day_idx]])[0]
                
                # Seasonal component (day of week)
                dow = future_date.dayofweek
                seasonal_value = daily_avg.get(dow, 0)
                
                # Weighted combination
                forecast_value = (trend_value * 0.7) + (seasonal_value * 0.3)
                
                # Ensure non-negative
                forecast_value = max(0, forecast_value)
                
                forecast.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'forecast': float(forecast_value),
                    'lower_bound': float(forecast_value * 0.8),
                    'upper_bound': float(forecast_value * 1.2)
                })
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting revenue: {e}")
            return self._generate_simple_forecast(historical_data, periods)
    
    def _generate_simple_forecast(self, historical_data: pd.DataFrame, periods: int) -> List[Dict[str, Any]]:
        """
        Generate simple forecast when ML models fail.
        
        Args:
            historical_data: Historical data
            periods: Number of periods
        
        Returns:
            List of forecasted values
        """
        if historical_data.empty:
            # Default values
            base_value = 1000
            growth_rate = 0.01
        else:
            base_value = historical_data['revenue'].mean()
            # Calculate simple growth rate
            if len(historical_data) > 1:
                growth_rate = (historical_data['revenue'].iloc[-1] - historical_data['revenue'].iloc[0]) / len(historical_data)
                growth_rate = max(0.001, growth_rate / base_value)
            else:
                growth_rate = 0.01
        
        forecast = []
        last_date = datetime.now()
        
        for i in range(1, periods + 1):
            future_date = last_date + timedelta(days=i)
            value = base_value * (1 + growth_rate * i)
            
            forecast.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'forecast': float(value),
                'lower_bound': float(value * 0.7),
                'upper_bound': float(value * 1.3)
            })
        
        return forecast
    
    def forecast_retention(self, retention_data: pd.DataFrame, periods: int = 30) -> List[float]:
        """
        Forecast retention rates.
        
        Args:
            retention_data: Historical retention data
            periods: Number of periods
        
        Returns:
            List of forecasted retention rates
        """
        try:
            if retention_data.empty or len(retention_data) < 3:
                return [0.6] * periods
            
            # Use exponential smoothing
            values = retention_data['retention'].values
            alpha = 0.3  # Smoothing factor
            
            forecast = []
            last_value = values[-1]
            
            for _ in range(periods):
                last_value = alpha * last_value + (1 - alpha) * np.mean(values[-3:])
                forecast.append(float(last_value))
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting retention: {e}")
            return [0.5] * periods
    
    def forecast_growth(self, data: pd.DataFrame, metric: str, periods: int = 30) -> List[float]:
        """
        Forecast growth for any metric.
        
        Args:
            data: Historical data
            metric: Metric column name
            periods: Number of periods
        
        Returns:
            List of forecasted values
        """
        try:
            if metric not in data.columns:
                return [0] * periods
            
            values = data[metric].values
            
            if len(values) < 2:
                return [values[0]] * periods if len(values) > 0 else [0] * periods
            
            # Calculate growth rate
            growth_rate = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0
            
            forecast = []
            for i in range(1, periods + 1):
                predicted = values[-1] + growth_rate * i
                forecast.append(float(max(0, predicted)))
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting growth: {e}")
            return [0] * periods