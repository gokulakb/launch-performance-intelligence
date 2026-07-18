"""
Retention analytics module for user retention and churn analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from database.queries import Queries
from analytics.churn import ChurnPredictor

logger = logging.getLogger(__name__)

class RetentionAnalytics:
    """User retention and churn analysis."""
    
    def __init__(self):
        self.queries = Queries()
        self.churn_predictor = ChurnPredictor()
    
    def get_retention_summary(self, company: str = None) -> Dict[str, Any]:
        """
        Get retention summary with key metrics.
        
        Args:
            company: Optional company filter
        
        Returns:
            Dictionary with retention metrics
        """
        try:
            # Get retention data
            retention_df = self.queries.get_retention_rates(company)
            
            if retention_df.empty:
                return {
                    'retention_d1': 0,
                    'retention_d7': 0,
                    'retention_d30': 0,
                    'retention_w4': 0,
                    'retention_monthly': 0,
                    'churn_rate': 0,
                    'total_users': 0,
                    'retention_trend': 'stable'
                }
            
            # Get latest cohort
            latest = retention_df.iloc[-1] if not retention_df.empty else {}
            
            # Calculate churn rate
            churn_df = self.queries.get_churn_metrics(company)
            churn_rate = churn_df['churn_rate'].mean() if not churn_df.empty else 0
            
            # Calculate trend
            trend = self._calculate_retention_trend(retention_df)
            
            return {
                'retention_d1': float(latest.get('retention_rate_d1', 0)),
                'retention_d7': float(latest.get('retention_rate_d7', 0)),
                'retention_d30': float(latest.get('retention_rate_d30', 0)),
                'retention_w4': float(latest.get('retention_rate_w4', 0)),
                'retention_monthly': float(latest.get('retention_rate_monthly', 0)),
                'churn_rate': churn_rate,
                'total_users': int(latest.get('total_users', 0)),
                'retention_trend': trend,
                'cohorts': retention_df['cohort'].tolist() if 'cohort' in retention_df else []
            }
            
        except Exception as e:
            logger.error(f"Error getting retention summary: {e}")
            return {}
    
    def get_cohort_heatmap_data(self, company: str = None) -> pd.DataFrame:
        """
        Get data for cohort retention heatmap.
        
        Args:
            company: Optional company filter
        
        Returns:
            DataFrame with cohort retention data
        """
        return self.queries.get_cohort_analysis(company)
    
    def get_retention_curve(self, company: str = None, days: int = 90) -> Dict[str, Any]:
        """
        Get retention curve data.
        
        Args:
            company: Optional company filter
            days: Number of days to analyze
        
        Returns:
            Dictionary with retention curve data
        """
        try:
            # Get retention data
            retention_df = self.queries.get_retention_rates(company)
            
            if retention_df.empty:
                return {'days': [], 'retention': []}
            
            # Calculate average retention across cohorts
            days_mapping = {
                'day_1_retained': 1,
                'day_7_retained': 7,
                'day_30_retained': 30,
                'week_4_retained': 28,
                'monthly_retained': 30
            }
            
            curve_data = []
            for col, day in days_mapping.items():
                if col in retention_df.columns:
                    avg_retention = retention_df[col].mean() * 100
                    curve_data.append({'day': day, 'retention': avg_retention})
            
            # Sort by day
            curve_data = sorted(curve_data, key=lambda x: x['day'])
            
            return {
                'days': [d['day'] for d in curve_data],
                'retention': [d['retention'] for d in curve_data]
            }
            
        except Exception as e:
            logger.error(f"Error getting retention curve: {e}")
            return {'days': [], 'retention': []}
    
    def get_churn_analysis(self, company: str = None) -> Dict[str, Any]:
        """
        Get churn analysis data.
        
        Args:
            company: Optional company filter
        
        Returns:
            Dictionary with churn analysis
        """
        try:
            # Get churn data
            churn_df = self.queries.get_churn_metrics(company)
            
            if churn_df.empty:
                return {'churn_rate': 0, 'churn_trend': 'stable', 'churn_by_cohort': []}
            
            # Calculate churn trend
            churn_trend = self._calculate_churn_trend(churn_df)
            
            # Get churn by cohort
            churn_by_cohort = churn_df[['cohort', 'churn_rate']].to_dict('records')
            
            return {
                'churn_rate': float(churn_df['churn_rate'].mean()),
                'churn_trend': churn_trend,
                'churn_by_cohort': churn_by_cohort,
                'total_churned': int(churn_df['churned_users'].sum()) if 'churned_users' in churn_df else 0,
                'total_users': int(churn_df['total_users'].sum()) if 'total_users' in churn_df else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting churn analysis: {e}")
            return {}
    
    def predict_churn_risk(self, company: str = None) -> List[Dict[str, Any]]:
        """
        Predict churn risk for users.
        
        Args:
            company: Optional company filter
        
        Returns:
            List of users with churn risk scores
        """
        try:
            # Get user data
            from database.database import db
            
            query = """
                SELECT 
                    u.user_id,
                    u.name,
                    u.email,
                    u.company,
                    u.signup_date,
                    u.last_active,
                    COUNT(e.id) as event_count,
                    AVG(e.duration) as avg_session_duration,
                    MAX(e.timestamp) as last_event
                FROM users u
                LEFT JOIN events e ON u.user_id = e.user_id
                WHERE 1=1
            """
            params = {}
            
            if company:
                query += " AND u.company = :company"
                params['company'] = company
            
            query += " GROUP BY u.user_id"
            
            user_data = db.execute_query(query, params)
            
            if user_data.empty:
                return []
            
            # Prepare features for prediction
            features = self._prepare_churn_features(user_data)
            
            # Get predictions
            predictions = self.churn_predictor.predict_churn(features)
            
            # Combine with user info
            results = []
            for idx, (_, user) in enumerate(user_data.iterrows()):
                if idx < len(predictions):
                    results.append({
                        'user_id': user['user_id'],
                        'name': user['name'],
                        'email': user['email'],
                        'company': user['company'],
                        'churn_risk': float(predictions[idx]),
                        'risk_level': 'high' if predictions[idx] > 0.7 else 'medium' if predictions[idx] > 0.4 else 'low'
                    })
            
            return sorted(results, key=lambda x: x['churn_risk'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error predicting churn risk: {e}")
            return []
    
    def _prepare_churn_features(self, user_data: pd.DataFrame) -> np.ndarray:
        """Prepare features for churn prediction."""
        features = []
        
        for _, user in user_data.iterrows():
            # Days since last active
            if user['last_active']:
                days_inactive = (datetime.now() - pd.to_datetime(user['last_active'])).days
            else:
                days_inactive = 0
            
            # Account age
            if user['signup_date']:
                account_age = (datetime.now() - pd.to_datetime(user['signup_date'])).days
            else:
                account_age = 0
            
            # Engagement metrics
            event_count = user['event_count'] if pd.notna(user['event_count']) else 0
            avg_session = user['avg_session_duration'] if pd.notna(user['avg_session_duration']) else 0
            
            features.append([
                days_inactive,
                account_age,
                event_count,
                avg_session,
                1 if days_inactive > 30 else 0
            ])
        
        return np.array(features)
    
    def _calculate_retention_trend(self, retention_df: pd.DataFrame) -> str:
        """Calculate retention trend direction."""
        if retention_df.empty:
            return 'stable'
        
        # Check if retention rates are increasing or decreasing
        if 'retention_rate_d7' in retention_df.columns:
            values = retention_df['retention_rate_d7'].tail(4).tolist()
            if len(values) < 2:
                return 'stable'
            
            if values[-1] > values[0]:
                return 'increasing'
            elif values[-1] < values[0]:
                return 'decreasing'
        
        return 'stable'
    
    def _calculate_churn_trend(self, churn_df: pd.DataFrame) -> str:
        """Calculate churn trend direction."""
        if churn_df.empty or 'churn_rate' not in churn_df.columns:
            return 'stable'
        
        values = churn_df['churn_rate'].tail(4).tolist()
        if len(values) < 2:
            return 'stable'
        
        if values[-1] < values[0]:
            return 'decreasing'
        elif values[-1] > values[0]:
            return 'increasing'
        
        return 'stable'