"""
Funnel analysis module for tracking user conversion through stages.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from database.queries import Queries

logger = logging.getLogger(__name__)

class FunnelAnalytics:
    """Funnel analysis for user journey tracking."""
    
    FUNNEL_STAGES = [
        'visitor',
        'signup',
        'profile_complete',
        'application',
        'interview',
        'offer',
        'hire'
    ]
    
    STAGE_LABELS = {
        'visitor': 'Visitors',
        'signup': 'Signups',
        'profile_complete': 'Profile Complete',
        'application': 'Applications',
        'interview': 'Interviews',
        'offer': 'Offers',
        'hire': 'Hired'
    }
    
    def __init__(self):
        self.queries = Queries()
    
    def get_funnel_data(self, company: str = None, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """
        Get complete funnel data with all stages.
        
        Args:
            company: Optional company filter
            date_from: Start date
            date_to: End date
        
        Returns:
            Dictionary with funnel data and calculations
        """
        try:
            # Get raw event data
            event_counts = self.queries.get_event_funnel(company, date_from, date_to)
            
            # Create funnel data
            funnel_data = {
                'stages': [],
                'counts': [],
                'drop_off': [],
                'conversion_rate': [],
                'labels': []
            }
            
            previous_count = None
            
            for stage in self.FUNNEL_STAGES:
                count = event_counts.get(stage, 0)
                label = self.STAGE_LABELS.get(stage, stage)
                
                funnel_data['stages'].append(stage)
                funnel_data['counts'].append(count)
                funnel_data['labels'].append(label)
                
                # Calculate drop-off
                if previous_count is not None and previous_count > 0:
                    drop_off = ((previous_count - count) / previous_count) * 100
                else:
                    drop_off = 0
                
                funnel_data['drop_off'].append(drop_off)
                
                # Calculate conversion rate
                if event_counts.get('visitor', 0) > 0:
                    conversion_rate = (count / event_counts.get('visitor', 1)) * 100
                else:
                    conversion_rate = 0
                
                funnel_data['conversion_rate'].append(conversion_rate)
                
                previous_count = count
            
            # Add summary metrics
            funnel_data['summary'] = {
                'total_visitors': event_counts.get('visitor', 0),
                'total_signups': event_counts.get('signup', 0),
                'total_hires': event_counts.get('hire', 0),
                'overall_conversion': self._calculate_overall_conversion(event_counts),
                'avg_time_to_hire': self._calculate_avg_time_to_hire(company, date_from, date_to)
            }
            
            return funnel_data
            
        except Exception as e:
            logger.error(f"Error getting funnel data: {e}")
            return {'stages': [], 'counts': [], 'drop_off': [], 'conversion_rate': [], 'labels': []}
    
    def get_stage_timeline(self, company: str = None, days: int = 30) -> pd.DataFrame:
        """
        Get timeline data for each funnel stage.
        
        Args:
            company: Optional company filter
            days: Number of days to look back
        
        Returns:
            DataFrame with stage counts over time
        """
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Build query for stage timelines
        query = """
            SELECT 
                DATE(timestamp) as date,
                event_type,
                COUNT(DISTINCT user_id) as count
            FROM events
            WHERE event_type IN :event_types
            AND timestamp >= :date_from
        """
        params = {
            'event_types': tuple(self.FUNNEL_STAGES),
            'date_from': date_from
        }
        
        if company:
            query += " AND user_id IN (SELECT user_id FROM users WHERE company = :company)"
            params['company'] = company
        
        query += " GROUP BY DATE(timestamp), event_type ORDER BY date, event_type"
        
        result = self.queries.db.execute_query(query, params)
        
        if result.empty:
            return pd.DataFrame(columns=['date', 'event_type', 'count'])
        
        # Pivot to get stages as columns
        timeline_df = result.pivot(index='date', columns='event_type', values='count').fillna(0)
        
        return timeline_df
    
    def get_conversion_matrix(self, company: str = None) -> pd.DataFrame:
        """
        Get conversion matrix between stages.
        
        Args:
            company: Optional company filter
        
        Returns:
            DataFrame with conversion rates between stages
        """
        funnel_data = self.get_funnel_data(company)
        stages = funnel_data['stages']
        counts = funnel_data['counts']
        
        # Create matrix
        matrix = np.zeros((len(stages), len(stages)))
        
        for i, from_count in enumerate(counts):
            for j, to_count in enumerate(counts):
                if i < j and from_count > 0:
                    matrix[i][j] = (to_count / from_count) * 100
        
        # Create DataFrame
        df = pd.DataFrame(
            matrix,
            index=[self.STAGE_LABELS.get(s, s) for s in stages],
            columns=[self.STAGE_LABELS.get(s, s) for s in stages]
        )
        
        return df
    
    def get_bottlenecks(self, company: str = None) -> List[Dict[str, Any]]:
        """
        Identify bottlenecks in the funnel.
        
        Args:
            company: Optional company filter
        
        Returns:
            List of bottlenecks with details
        """
        funnel_data = self.get_funnel_data(company)
        bottlenecks = []
        
        for i, (stage, drop_off) in enumerate(zip(funnel_data['stages'], funnel_data['drop_off'])):
            if drop_off > 50:  # More than 50% drop-off
                bottlenecks.append({
                    'stage': self.STAGE_LABELS.get(stage, stage),
                    'drop_off': drop_off,
                    'severity': 'high' if drop_off > 70 else 'medium',
                    'impact': self._calculate_impact(funnel_data, i)
                })
        
        return sorted(bottlenecks, key=lambda x: x['drop_off'], reverse=True)
    
    def _calculate_overall_conversion(self, event_counts: Dict[str, int]) -> float:
        """Calculate overall conversion from visitor to hire."""
        visitors = event_counts.get('visitor', 0)
        hires = event_counts.get('hire', 0)
        
        if visitors == 0:
            return 0
        
        return (hires / visitors) * 100
    
    def _calculate_avg_time_to_hire(self, company: str = None, date_from: str = None, date_to: str = None) -> float:
        """Calculate average time from signup to hire."""
        # This would require tracking user journey times
        # For now, return a placeholder
        return 30.5
    
    def _calculate_impact(self, funnel_data: Dict[str, Any], stage_index: int) -> float:
        """Calculate impact score for a bottleneck."""
        counts = funnel_data['counts']
        if stage_index < len(counts) - 1:
            current = counts[stage_index]
            next_stage = counts[stage_index + 1]
            if current > 0:
                return (current - next_stage) / current * 100
        return 0
    
    def get_funnel_summary(self, company: str = None) -> Dict[str, Any]:
        """
        Get a summary of funnel performance.
        
        Args:
            company: Optional company filter
        
        Returns:
            Dictionary with funnel summary statistics
        """
        funnel_data = self.get_funnel_data(company)
        
        summary = {
            'total_visitors': funnel_data['counts'][0] if funnel_data['counts'] else 0,
            'total_hires': funnel_data['counts'][-1] if funnel_data['counts'] else 0,
            'overall_conversion': funnel_data['conversion_rate'][-1] if funnel_data['conversion_rate'] else 0,
            'worst_bottleneck': None,
            'avg_drop_off': np.mean(funnel_data['drop_off']) if funnel_data['drop_off'] else 0,
            'best_performing_stage': None
        }
        
        # Find worst bottleneck
        if funnel_data['drop_off']:
            max_idx = np.argmax(funnel_data['drop_off'])
            summary['worst_bottleneck'] = {
                'stage': funnel_data['labels'][max_idx],
                'drop_off': funnel_data['drop_off'][max_idx]
            }
        
        # Find best performing stage
        if funnel_data['conversion_rate']:
            # Find stage with highest increase in conversion
            rates = funnel_data['conversion_rate']
            best_idx = np.argmax(rates[1:] - rates[:-1]) + 1 if len(rates) > 1 else 0
            summary['best_performing_stage'] = funnel_data['labels'][best_idx]
        
        return summary