"""
Problem ranking module for identifying and prioritizing issues.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from database.queries import Queries
from analytics.revenue import RevenueAnalytics
from analytics.retention import RetentionAnalytics
from analytics.funnel import FunnelAnalytics
from analytics.quality import QualityAnalytics
from analytics.anomalies import AnomalyDetector

logger = logging.getLogger(__name__)

class ProblemRanking:
    """Automatic problem identification and ranking."""
    
    def __init__(self):
        self.queries = Queries()
        self.revenue = RevenueAnalytics()
        self.retention = RetentionAnalytics()
        self.funnel = FunnelAnalytics()
        self.quality = QualityAnalytics()
        self.anomaly_detector = AnomalyDetector()
    
    def rank_problems(self, company: str = None) -> List[Dict[str, Any]]:
        """
        Rank problems by impact and urgency.
        
        Args:
            company: Optional company filter
        
        Returns:
            List of problems with ranking and details
        """
        problems = []
        
        try:
            # Revenue problems
            revenue_problems = self._identify_revenue_problems(company)
            problems.extend(revenue_problems)
            
            # Retention problems
            retention_problems = self._identify_retention_problems(company)
            problems.extend(retention_problems)
            
            # Funnel problems
            funnel_problems = self._identify_funnel_problems(company)
            problems.extend(funnel_problems)
            
            # Quality problems
            quality_problems = self._identify_quality_problems()
            problems.extend(quality_problems)
            
            # Anomaly problems
            anomaly_problems = self._identify_anomaly_problems(company)
            problems.extend(anomaly_problems)
            
            # Calculate impact scores
            for problem in problems:
                problem['impact_score'] = self._calculate_impact_score(problem)
            
            # Rank by impact
            problems = sorted(problems, key=lambda x: x['impact_score'], reverse=True)
            
            # Add ranking
            for i, problem in enumerate(problems, 1):
                problem['rank'] = i
            
            return problems
            
        except Exception as e:
            logger.error(f"Error ranking problems: {e}")
            return []
    
    def _identify_revenue_problems(self, company: str = None) -> List[Dict[str, Any]]:
        """Identify revenue-related problems."""
        problems = []
        
        try:
            overview = self.revenue.get_revenue_overview(company)
            
            # Check revenue decline
            if overview.get('revenue_growth', 0) < -10:
                problems.append({
                    'category': 'Revenue',
                    'title': 'Revenue Decline',
                    'description': f"Revenue declined by {abs(overview['revenue_growth']):.1f}%",
                    'evidence': f"Revenue growth: {overview['revenue_growth']:.1f}%",
                    'business_impact': high,
                    'customer_impact': 'medium',
                    'engineering_cost': 'medium',
                    'priority': 'high',
                    'severity': 'critical',
                    'suggested_action': 'Analyze revenue drivers and identify causes of decline',
                    'owner': 'Revenue Team',
                    'eta': '2 weeks'
                })
            
            # Check transaction volume
            if overview.get('total_transactions', 0) < 100:
                problems.append({
                    'category': 'Revenue',
                    'title': 'Low Transaction Volume',
                    'description': f"Only {overview['total_transactions']} transactions recorded",
                    'evidence': f"Transaction count: {overview['total_transactions']}",
                    'business_impact': 'high',
                    'customer_impact': 'medium',
                    'engineering_cost': 'low',
                    'priority': 'high',
                    'severity': 'high',
                    'suggested_action': 'Investigate root cause of low transaction volume',
                    'owner': 'Revenue Team',
                    'eta': '1 week'
                })
            
        except Exception as e:
            logger.error(f"Error identifying revenue problems: {e}")
        
        return problems
    
    def _identify_retention_problems(self, company: str = None) -> List[Dict[str, Any]]:
        """Identify retention-related problems."""
        problems = []
        
        try:
            retention_summary = self.retention.get_retention_summary(company)
            
            # Check retention rates
            if retention_summary.get('retention_d30', 0) < 20:
                problems.append({
                    'category': 'Retention',
                    'title': 'Poor Long-term Retention',
                    'description': f"Day 30 retention is only {retention_summary['retention_d30']:.1f}%",
                    'evidence': f"D30 retention: {retention_summary['retention_d30']:.1f}%",
                    'business_impact': 'high',
                    'customer_impact': 'high',
                    'engineering_cost': 'high',
                    'priority': 'critical',
                    'severity': 'critical',
                    'suggested_action': 'Implement retention strategies and improve onboarding',
                    'owner': 'Product Team',
                    'eta': '1 month'
                })
            
            # Check churn rate
            if retention_summary.get('churn_rate', 0) > 30:
                problems.append({
                    'category': 'Retention',
                    'title': 'High Churn Rate',
                    'description': f"Churn rate is {retention_summary['churn_rate']:.1f}%",
                    'evidence': f"Churn rate: {retention_summary['churn_rate']:.1f}%",
                    'business_impact': 'critical',
                    'customer_impact': 'high',
                    'engineering_cost': 'medium',
                    'priority': 'critical',
                    'severity': 'critical',
                    'suggested_action': 'Analyze churn drivers and implement retention campaigns',
                    'owner': 'Customer Success',
                    'eta': '3 weeks'
                })
            
        except Exception as e:
            logger.error(f"Error identifying retention problems: {e}")
        
        return problems
    
    def _identify_funnel_problems(self, company: str = None) -> List[Dict[str, Any]]:
        """Identify funnel-related problems."""
        problems = []
        
        try:
            funnel_summary = self.funnel.get_funnel_summary(company)
            
            # Check overall conversion
            if funnel_summary.get('overall_conversion', 0) < 5:
                problems.append({
                    'category': 'Funnel',
                    'title': 'Low Overall Conversion',
                    'description': f"Overall conversion rate is {funnel_summary['overall_conversion']:.1f}%",
                    'evidence': f"Conversion rate: {funnel_summary['overall_conversion']:.1f}%",
                    'business_impact': 'critical',
                    'customer_impact': 'high',
                    'engineering_cost': 'high',
                    'priority': 'critical',
                    'severity': 'critical',
                    'suggested_action': 'Optimize entire user journey and identify drop-off points',
                    'owner': 'Product Team',
                    'eta': '1 month'
                })
            
            # Check bottlenecks
            bottleneck = funnel_summary.get('worst_bottleneck')
            if bottleneck and bottleneck['drop_off'] > 70:
                problems.append({
                    'category': 'Funnel',
                    'title': f'Bottleneck at {bottleneck["stage"]}',
                    'description': f"{bottleneck['drop_off']:.1f}% drop-off at {bottleneck['stage']}",
                    'evidence': f"Drop-off rate: {bottleneck['drop_off']:.1f}%",
                    'business_impact': 'high',
                    'customer_impact': 'medium',
                    'engineering_cost': 'medium',
                    'priority': 'high',
                    'severity': 'high',
                    'suggested_action': f'Improve {bottleneck["stage"]} experience',
                    'owner': 'Product Team',
                    'eta': '2 weeks'
                })
            
        except Exception as e:
            logger.error(f"Error identifying funnel problems: {e}")
        
        return problems
    
    def _identify_quality_problems(self) -> List[Dict[str, Any]]:
        """Identify data quality problems."""
        problems = []
        
        try:
            quality_summary = self.quality.get_quality_summary()
            
            if quality_summary.get('overall_score', 0) < 0.8:
                problems.append({
                    'category': 'Quality',
                    'title': 'Poor Data Quality',
                    'description': f"Overall quality score is {quality_summary['overall_score']:.1%}",
                    'evidence': f"Quality score: {quality_summary['overall_score']:.1%}",
                    'business_impact': 'medium',
                    'customer_impact': 'medium',
                    'engineering_cost': 'high',
                    'priority': 'medium',
                    'severity': 'high',
                    'suggested_action': 'Implement data validation and cleaning processes',
                    'owner': 'Data Engineering',
                    'eta': '3 weeks'
                })
            
            # Check specific issues
            for metric in quality_summary.get('metrics', []):
                if metric['value'] < 0.7:
                    problems.append({
                        'category': 'Quality',
                        'title': f'Quality Issue: {metric["metric_type"]}',
                        'description': f"{metric['metric_type']} score is {metric['value']:.1%} in {metric['table_name']}",
                        'evidence': f"Score: {metric['value']:.1%}",
                        'business_impact': 'medium',
                        'customer_impact': 'low',
                        'engineering_cost': 'medium',
                        'priority': 'medium',
                        'severity': 'medium',
                        'suggested_action': f'Fix {metric["metric_type"]} issues in {metric["table_name"]}',
                        'owner': 'Data Engineering',
                        'eta': '1 week'
                    })
            
        except Exception as e:
            logger.error(f"Error identifying quality problems: {e}")
        
        return problems
    
    def _identify_anomaly_problems(self, company: str = None) -> List[Dict[str, Any]]:
        """Identify anomaly-related problems."""
        problems = []
        
        try:
            # Get revenue data for anomaly detection
            overview = self.revenue.get_revenue_overview(company)
            revenue_data = overview.get('revenue_data')
            
            if revenue_data is not None and not revenue_data.empty:
                # Detect spikes
                spikes = self.anomaly_detector.detect_spikes(revenue_data['revenue'].tolist())
                
                if spikes:
                    problems.append({
                        'category': 'Anomaly',
                        'title': 'Revenue Spikes Detected',
                        'description': f"Detected {len(spikes)} unusual revenue spikes",
                        'evidence': f"Spikes at: {', '.join([str(s) for s in spikes[:5]])}",
                        'business_impact': 'medium',
                        'customer_impact': 'low',
                        'engineering_cost': 'low',
                        'priority': 'medium',
                        'severity': 'medium',
                        'suggested_action': 'Investigate causes of revenue spikes',
                        'owner': 'Revenue Team',
                        'eta': '1 week'
                    })
                
                # Detect drops
                drops = self.anomaly_detector.detect_drops(revenue_data['revenue'].tolist())
                
                if drops:
                    problems.append({
                        'category': 'Anomaly',
                        'title': 'Revenue Drops Detected',
                        'description': f"Detected {len(drops)} unusual revenue drops",
                        'evidence': f"Drops at: {', '.join([str(d) for d in drops[:5]])}",
                        'business_impact': 'high',
                        'customer_impact': 'medium',
                        'engineering_cost': 'medium',
                        'priority': 'high',
                        'severity': 'high',
                        'suggested_action': 'Investigate causes of revenue drops',
                        'owner': 'Revenue Team',
                        'eta': '1 week'
                    })
            
        except Exception as e:
            logger.error(f"Error identifying anomaly problems: {e}")
        
        return problems
    
    def _calculate_impact_score(self, problem: Dict[str, Any]) -> float:
        """
        Calculate impact score for problem ranking.
        
        Args:
            problem: Problem dictionary
        
        Returns:
            Impact score (0-100)
        """
        impact_weights = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25
        }
        
        priority_weights = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25
        }
        
        severity_weights = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25
        }
        
        business_impact = impact_weights.get(problem.get('business_impact', 'medium'), 50)
        customer_impact = impact_weights.get(problem.get('customer_impact', 'medium'), 50)
        priority = priority_weights.get(problem.get('priority', 'medium'), 50)
        severity = severity_weights.get(problem.get('severity', 'medium'), 50)
        
        # Weighted average
        score = (business_impact * 0.3 + 
                 customer_impact * 0.2 + 
                 priority * 0.25 + 
                 severity * 0.25)
        
        return score