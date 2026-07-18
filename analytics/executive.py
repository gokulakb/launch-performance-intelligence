"""
Executive Dashboard analytics module.
Provides high-level metrics and KPIs for executive monitoring.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from database.queries import Queries
from utils.metrics import MetricsCalculator
from utils.validation import Validator

logger = logging.getLogger(__name__)

class ExecutiveAnalytics:
    """Executive-level analytics and KPI calculations."""
    
    def __init__(self):
        self.queries = Queries()
        self.metrics = MetricsCalculator()
        self.validator = Validator()
    
    def get_executive_summary(self, company: str = None) -> Dict[str, Any]:
        """
        Get executive summary with all key metrics.
        
        Args:
            company: Optional company filter
        
        Returns:
            Dictionary containing all executive metrics
        """
        summary = {}
        
        try:
            # Get raw data
            users_df = self.queries.get_user_metrics(company)
            revenue_df = self.queries.get_revenue_by_date(company)
            retention_df = self.queries.get_retention_rates(company)
            launch_df = self.queries.get_launch_metrics(company)
            
            # Calculate core metrics
            summary['timestamp'] = datetime.now().isoformat()
            summary['company'] = company or 'All Companies'
            
            # User metrics
            summary['total_users'] = int(users_df['total_users'].iloc[0]) if not users_df.empty else 0
            summary['active_users'] = int(users_df['active_users'].iloc[0]) if not users_df.empty else 0
            summary['profile_completion_rate'] = float(users_df['completion_rate'].iloc[0]) if not users_df.empty else 0
            
            # Revenue metrics
            if not revenue_df.empty:
                summary['total_revenue'] = float(revenue_df['revenue'].sum())
                summary['avg_daily_revenue'] = float(revenue_df['revenue'].mean())
                summary['revenue_trend'] = self._calculate_trend(revenue_df['revenue'].tolist())
            
            # Retention metrics
            if not retention_df.empty:
                latest = retention_df.iloc[-1]
                summary['retention_d1'] = float(latest.get('retention_rate_d1', 0))
                summary['retention_d7'] = float(latest.get('retention_rate_d7', 0))
                summary['retention_d30'] = float(latest.get('retention_rate_d30', 0))
                summary['churn_rate'] = float(latest.get('churn_rate', 0)) if 'churn_rate' in latest else 0
            
            # Launch metrics
            if not launch_df.empty:
                latest_launch = launch_df.iloc[-1]
                summary['signups'] = int(latest_launch.get('signups', 0))
                summary['applications'] = int(latest_launch.get('applications', 0))
                summary['interviews'] = int(latest_launch.get('interviews', 0))
                summary['offers'] = int(latest_launch.get('offers', 0))
                summary['hires'] = int(latest_launch.get('hires', 0))
                summary['quality_score'] = float(latest_launch.get('quality_score', 0))
            
            # Calculate derived metrics
            summary['conversion_rate'] = self._calculate_conversion_rate(summary)
            summary['revenue_per_user'] = summary['total_revenue'] / summary['total_users'] if summary['total_users'] > 0 else 0
            summary['engagement_score'] = self._calculate_engagement_score(summary)
            
            # Add validation
            summary['validation_status'] = self.validator.validate_metrics(summary)
            
        except Exception as e:
            logger.error(f"Error getting executive summary: {e}")
            summary['error'] = str(e)
        
        return summary
    
    def get_kpi_cards(self, company: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Get KPI card data for dashboard.
        
        Returns:
            Dictionary of KPI cards with values, trends, and status
        """
        summary = self.get_executive_summary(company)
        
        kpi_cards = {
            'visitors': {
                'value': summary.get('total_users', 0),
                'trend': summary.get('revenue_trend', 0),
                'status': 'success' if summary.get('total_users', 0) > 1000 else 'warning'
            },
            'active_users': {
                'value': summary.get('active_users', 0),
                'trend': summary.get('active_trend', 0),
                'status': 'success' if summary.get('active_users', 0) > 500 else 'warning'
            },
            'signups': {
                'value': summary.get('signups', 0),
                'trend': 0,
                'status': 'success' if summary.get('signups', 0) > 100 else 'warning'
            },
            'applications': {
                'value': summary.get('applications', 0),
                'trend': 0,
                'status': 'success' if summary.get('applications', 0) > 50 else 'warning'
            },
            'interviews': {
                'value': summary.get('interviews', 0),
                'trend': 0,
                'status': 'success' if summary.get('interviews', 0) > 20 else 'warning'
            },
            'offers': {
                'value': summary.get('offers', 0),
                'trend': 0,
                'status': 'success' if summary.get('offers', 0) > 10 else 'warning'
            },
            'hires': {
                'value': summary.get('hires', 0),
                'trend': 0,
                'status': 'success' if summary.get('hires', 0) > 5 else 'warning'
            },
            'revenue': {
                'value': summary.get('total_revenue', 0),
                'trend': summary.get('revenue_trend', 0),
                'status': 'success' if summary.get('total_revenue', 0) > 100000 else 'warning'
            },
            'retention': {
                'value': summary.get('retention_d7', 0),
                'trend': 0,
                'status': 'success' if summary.get('retention_d7', 0) > 70 else 'warning'
            },
            'quality_score': {
                'value': summary.get('quality_score', 0),
                'trend': 0,
                'status': 'success' if summary.get('quality_score', 0) > 80 else 'warning'
            }
        }
        
        return kpi_cards
    
    def get_trend_data(self, company: str = None, days: int = 30) -> pd.DataFrame:
        """
        Get trend data for charts.
        
        Args:
            company: Optional company filter
            days: Number of days of trend data
        
        Returns:
            DataFrame with trend data
        """
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get launch metrics
        launch_df = self.queries.get_launch_metrics(company, date_from)
        
        if launch_df.empty:
            # Create empty DataFrame with expected columns
            columns = ['metric_date', 'visitors', 'active_users', 'signups', 
                      'applications', 'interviews', 'offers', 'hires', 
                      'revenue', 'retention_rate', 'quality_score']
            return pd.DataFrame(columns=columns)
        
        return launch_df
    
    def _calculate_trend(self, values: list) -> float:
        """Calculate trend percentage."""
        if len(values) < 2:
            return 0
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = np.mean(first_half) if first_half else 0
        avg_second = np.mean(second_half) if second_half else 0
        
        if avg_first == 0:
            return 0
        
        return ((avg_second - avg_first) / avg_first) * 100
    
    def _calculate_conversion_rate(self, summary: Dict[str, Any]) -> float:
        """Calculate overall conversion rate."""
        signups = summary.get('signups', 0)
        hires = summary.get('hires', 0)
        
        if signups == 0:
            return 0
        
        return (hires / signups) * 100
    
    def _calculate_engagement_score(self, summary: Dict[str, Any]) -> float:
        """Calculate engagement score based on multiple metrics."""
        scores = []
        
        # Active user ratio
        active_ratio = summary.get('active_users', 0) / summary.get('total_users', 1)
        scores.append(min(active_ratio * 100, 100))
        
        # Profile completion
        scores.append(summary.get('profile_completion_rate', 0))
        
        # Retention
        scores.append(summary.get('retention_d7', 0))
        
        return np.mean(scores)
    
    def get_company_comparison(self) -> pd.DataFrame:
        """Get company comparison data."""
        companies = ['TechCorp', 'DataFlow', 'CloudNine', 'SmartSolutions', 'InnovateLabs']
        comparison_data = []
        
        for company in companies:
            summary = self.get_executive_summary(company)
            comparison_data.append({
                'company': company,
                'total_users': summary.get('total_users', 0),
                'active_users': summary.get('active_users', 0),
                'total_revenue': summary.get('total_revenue', 0),
                'retention_d7': summary.get('retention_d7', 0),
                'quality_score': summary.get('quality_score', 0),
                'conversion_rate': summary.get('conversion_rate', 0)
            })
        
        return pd.DataFrame(comparison_data)