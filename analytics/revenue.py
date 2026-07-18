"""
Revenue analytics module for tracking and forecasting revenue.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from database.queries import Queries
from analytics.forecasting import RevenueForecaster

logger = logging.getLogger(__name__)

class RevenueAnalytics:
    """Revenue analysis and forecasting."""
    
    def __init__(self):
        self.queries = Queries()
        self.forecaster = RevenueForecaster()
    
    def get_revenue_overview(self, company: str = None, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """
        Get comprehensive revenue overview.
        
        Args:
            company: Optional company filter
            date_from: Start date
            date_to: End date
        
        Returns:
            Dictionary with revenue metrics
        """
        try:
            # Get revenue data
            revenue_df = self.queries.get_revenue_by_date(company, date_from, date_to)
            
            if revenue_df.empty:
                return {
                    'total_revenue': 0,
                    'avg_daily_revenue': 0,
                    'avg_transaction': 0,
                    'total_transactions': 0,
                    'mrr': 0,
                    'revenue_growth': 0,
                    'peak_day': None,
                    'peak_revenue': 0
                }
            
            # Calculate metrics
            total_revenue = revenue_df['revenue'].sum()
            total_transactions = revenue_df['transactions'].sum()
            avg_transaction = revenue_df['avg_transaction'].mean()
            avg_daily_revenue = revenue_df['revenue'].mean()
            
            # Calculate MRR
            mrr = self.queries.get_mrr(company)
            
            # Calculate growth
            half = len(revenue_df) // 2
            if half > 0:
                first_half_revenue = revenue_df['revenue'].iloc[:half].sum()
                second_half_revenue = revenue_df['revenue'].iloc[half:].sum()
                revenue_growth = ((second_half_revenue - first_half_revenue) / first_half_revenue * 100) if first_half_revenue > 0 else 0
            else:
                revenue_growth = 0
            
            # Find peak day
            peak_idx = revenue_df['revenue'].idxmax()
            peak_day = revenue_df.loc[peak_idx, 'date'] if not pd.isna(peak_idx) else None
            peak_revenue = revenue_df['revenue'].max()
            
            return {
                'total_revenue': total_revenue,
                'avg_daily_revenue': avg_daily_revenue,
                'avg_transaction': avg_transaction,
                'total_transactions': total_transactions,
                'mrr': mrr,
                'revenue_growth': revenue_growth,
                'peak_day': peak_day,
                'peak_revenue': peak_revenue,
                'revenue_data': revenue_df
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue overview: {e}")
            return {}
    
    def get_revenue_by_company(self, date_from: str = None, date_to: str = None) -> pd.DataFrame:
        """
        Get revenue breakdown by company.
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            DataFrame with revenue by company
        """
        return self.queries.get_revenue_by_company(date_from, date_to)
    
    def get_revenue_by_recruiter(self, company: str = None) -> pd.DataFrame:
        """
        Get revenue breakdown by recruiter.
        
        Args:
            company: Optional company filter
        
        Returns:
            DataFrame with revenue by recruiter
        """
        return self.queries.get_revenue_by_recruiter(company)
    
    def get_revenue_by_college(self, date_from: str = None, date_to: str = None) -> pd.DataFrame:
        """
        Get revenue breakdown by college.
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            DataFrame with revenue by college
        """
        query = """
            SELECT 
                college,
                SUM(amount) as revenue,
                COUNT(*) as transactions,
                AVG(amount) as avg_transaction
            FROM revenue
            WHERE 1=1
        """
        params = {}
        
        if date_from:
            query += " AND transaction_date >= :date_from"
            params['date_from'] = date_from
        if date_to:
            query += " AND transaction_date <= :date_to"
            params['date_to'] = date_to
        
        query += " GROUP BY college ORDER BY revenue DESC"
        
        return self.queries.db.execute_query(query, params)
    
    def get_revenue_trends(self, company: str = None, days: int = 90) -> Dict[str, Any]:
        """
        Get revenue trends with various aggregations.
        
        Args:
            company: Optional company filter
            days: Number of days to analyze
        
        Returns:
            Dictionary with daily, weekly, monthly trends
        """
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        revenue_df = self.queries.get_revenue_by_date(company, date_from)
        
        if revenue_df.empty:
            return {'daily': pd.DataFrame(), 'weekly': pd.DataFrame(), 'monthly': pd.DataFrame()}
        
        # Daily trend
        daily = revenue_df.copy()
        
        # Weekly trend
        daily['week'] = pd.to_datetime(daily['date']).dt.isocalendar().week
        weekly = daily.groupby('week').agg({
            'revenue': 'sum',
            'transactions': 'sum',
            'avg_transaction': 'mean'
        }).reset_index()
        weekly['date'] = pd.to_datetime(daily['date']).dt.year.astype(str) + '-W' + weekly['week'].astype(str)
        
        # Monthly trend
        daily['month'] = pd.to_datetime(daily['date']).dt.to_period('M')
        monthly = daily.groupby('month').agg({
            'revenue': 'sum',
            'transactions': 'sum',
            'avg_transaction': 'mean'
        }).reset_index()
        monthly['date'] = monthly['month'].astype(str)
        
        return {
            'daily': daily,
            'weekly': weekly,
            'monthly': monthly
        }
    
    def get_revenue_forecast(self, company: str = None, periods: int = 30) -> Dict[str, Any]:
        """
        Get revenue forecast using ML.
        
        Args:
            company: Optional company filter
            periods: Number of periods to forecast
        
        Returns:
            Dictionary with forecast data
        """
        try:
            # Get historical data
            date_from = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            revenue_df = self.queries.get_revenue_by_date(company, date_from)
            
            if revenue_df.empty:
                return {'forecast': [], 'error': 'No data available for forecasting'}
            
            # Prepare data
            data = revenue_df[['date', 'revenue']].copy()
            data['date'] = pd.to_datetime(data['date'])
            data = data.sort_values('date')
            
            # Forecast
            forecast = self.forecaster.forecast_revenue(data, periods)
            
            return {
                'historical': data.to_dict('records'),
                'forecast': forecast,
                'accuracy': 0.85  # Placeholder for model accuracy
            }
            
        except Exception as e:
            logger.error(f"Error generating revenue forecast: {e}")
            return {'forecast': [], 'error': str(e)}
    
    def calculate_revenue_kpis(self, company: str = None) -> Dict[str, Any]:
        """
        Calculate revenue KPIs.
        
        Args:
            company: Optional company filter
        
        Returns:
            Dictionary with revenue KPIs
        """
        overview = self.get_revenue_overview(company)
        
        kpis = {
            'total_revenue': overview.get('total_revenue', 0),
            'mrr': overview.get('mrr', 0),
            'arr': overview.get('mrr', 0) * 12,
            'avg_daily_revenue': overview.get('avg_daily_revenue', 0),
            'revenue_growth': overview.get('revenue_growth', 0),
            'avg_transaction': overview.get('avg_transaction', 0),
            'transaction_volume': overview.get('total_transactions', 0),
            'peak_revenue_day': overview.get('peak_day', None)
        }
        
        return kpis