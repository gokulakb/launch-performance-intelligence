"""
Data quality analytics module for monitoring data health.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
import re
import logging

from database.queries import Queries
from database.database import db

logger = logging.getLogger(__name__)

class QualityAnalytics:
    """Data quality monitoring and analysis."""
    
    def __init__(self):
        self.queries = Queries()
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive quality summary.
        
        Returns:
            Dictionary with quality metrics
        """
        try:
            quality_df = self.queries.get_quality_metrics()
            
            if quality_df.empty:
                return {
                    'overall_score': 0,
                    'completeness': 0,
                    'consistency': 0,
                    'accuracy': 0,
                    'validation_status': 'unknown',
                    'metrics': []
                }
            
            # Calculate overall scores
            completeness = quality_df[quality_df['metric_type'] == 'completeness']['value'].mean()
            consistency = quality_df[quality_df['metric_type'] == 'consistency']['value'].mean()
            accuracy = quality_df[quality_df['metric_type'] == 'accuracy']['value'].mean()
            
            overall_score = (completeness + consistency + accuracy) / 3
            
            return {
                'overall_score': float(overall_score) if not pd.isna(overall_score) else 0,
                'completeness': float(completeness) if not pd.isna(completeness) else 0,
                'consistency': float(consistency) if not pd.isna(consistency) else 0,
                'accuracy': float(accuracy) if not pd.isna(accuracy) else 0,
                'validation_status': 'valid' if overall_score > 0.9 else 'warning' if overall_score > 0.7 else 'critical',
                'metrics': quality_df.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error getting quality summary: {e}")
            return {}
    
    def get_table_quality(self, table_name: str) -> Dict[str, Any]:
        """
        Get quality metrics for a specific table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            Dictionary with table quality metrics
        """
        try:
            quality_df = self.queries.get_quality_metrics(table_name)
            
            if quality_df.empty:
                return {'table_name': table_name, 'quality_score': 0, 'issues': []}
            
            # Calculate table score
            completeness = quality_df[quality_df['metric_type'] == 'completeness']['value'].mean()
            consistency = quality_df[quality_df['metric_type'] == 'consistency']['value'].mean()
            
            # Identify issues
            issues = []
            for _, row in quality_df.iterrows():
                if row['value'] < 0.9:
                    issues.append({
                        'column': row['column_name'] if 'column_name' in row else 'unknown',
                        'metric': row['metric_type'],
                        'value': float(row['value']),
                        'issue': f"{row['metric_type']} issue detected"
                    })
            
            return {
                'table_name': table_name,
                'quality_score': float((completeness + consistency) / 2) if not pd.isna(completeness) else 0,
                'completeness': float(completeness) if not pd.isna(completeness) else 0,
                'consistency': float(consistency) if not pd.isna(consistency) else 0,
                'issues': issues,
                'total_rows': int(quality_df['total_count'].iloc[0]) if 'total_count' in quality_df else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting table quality for {table_name}: {e}")
            return {'table_name': table_name, 'quality_score': 0, 'issues': []}
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
    
    def detect_anomalies(self, df: pd.DataFrame, column: str, method: str = 'iqr') -> List[int]:
        """
        Detect anomalies in a column using statistical methods.
        
        Args:
            df: DataFrame
            column: Column name to analyze
            method: Detection method ('iqr' or 'zscore')
        
        Returns:
            List of indices with anomalies
        """
        try:
            values = df[column].dropna()
            
            if len(values) < 3:
                return []
            
            if method == 'iqr':
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                anomaly_mask = (values < lower_bound) | (values > upper_bound)
            
            elif method == 'zscore':
                z_scores = np.abs((values - values.mean()) / values.std())
                anomaly_mask = z_scores > 3
            
            else:
                return []
            
            return values.index[anomaly_mask].tolist()
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def detect_duplicates(self, df: pd.DataFrame, columns: List[str]) -> List[int]:
        """
        Detect duplicate records based on specified columns.
        
        Args:
            df: DataFrame
            columns: Columns to check for duplicates
        
        Returns:
            List of indices with duplicates
        """
        try:
            duplicates = df.duplicated(subset=columns, keep='first')
            return df[duplicates].index.tolist()
            
        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}")
            return []
    
    def get_data_quality_report(self, company: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.
        
        Args:
            company: Optional company filter
        
        Returns:
            Dictionary with quality report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'company': company or 'All',
            'overall_quality': self.get_quality_summary(),
            'table_quality': [],
            'issues_summary': {
                'critical': 0,
                'warning': 0,
                'info': 0
            }
        }
        
        # Get all tables
        try:
            tables = ['users', 'events', 'revenue', 'retention', 'launch_metrics']
            
            for table in tables:
                quality = self.get_table_quality(table)
                report['table_quality'].append(quality)
                
                # Count issues
                for issue in quality.get('issues', []):
                    if issue['value'] < 0.7:
                        report['issues_summary']['critical'] += 1
                    elif issue['value'] < 0.9:
                        report['issues_summary']['warning'] += 1
                    else:
                        report['issues_summary']['info'] += 1
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return report