"""
Data validation utilities.
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

class Validator:
    """Data validation and quality checking utilities."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, str(phone)))
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format."""
        patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$'   # MM-DD-YYYY
        ]
        for pattern in patterns:
            if re.match(pattern, str(date_str)):
                return True
        return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return bool(re.match(pattern, str(url)))
    
    @staticmethod
    def check_missing_values(df: pd.DataFrame, threshold: float = 0.1) -> Dict[str, float]:
        """
        Check missing values in DataFrame.
        
        Args:
            df: DataFrame to check
            threshold: Threshold for warning
        
        Returns:
            Dictionary of missing value percentages
        """
        missing_percent = {}
        
        for column in df.columns:
            missing = df[column].isna().sum()
            percent = (missing / len(df)) * 100
            missing_percent[column] = percent
        
        return missing_percent
    
    @staticmethod
    def check_duplicates(df: pd.DataFrame, subset: List[str] = None) -> Dict[str, Any]:
        """
        Check for duplicate rows.
        
        Args:
            df: DataFrame to check
            subset: Columns to check for duplicates
        
        Returns:
            Dictionary with duplicate information
        """
        if subset:
            duplicates = df.duplicated(subset=subset)
        else:
            duplicates = df.duplicated()
        
        duplicate_count = duplicates.sum()
        
        return {
            'count': duplicate_count,
            'percentage': (duplicate_count / len(df)) * 100 if len(df) > 0 else 0,
            'indices': df[duplicates].index.tolist()
        }
    
    @staticmethod
    def check_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> Dict[str, Any]:
        """
        Check for outliers in a column.
        
        Args:
            df: DataFrame
            column: Column to check
            method: Detection method ('iqr' or 'zscore')
        
        Returns:
            Dictionary with outlier information
        """
        values = df[column].dropna()
        
        if len(values) < 3:
            return {'count': 0, 'indices': [], 'percentage': 0}
        
        if method == 'iqr':
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_mask = (values < lower_bound) | (values > upper_bound)
        elif method == 'zscore':
            z_scores = np.abs((values - values.mean()) / values.std())
            outlier_mask = z_scores > 3
        else:
            return {'count': 0, 'indices': [], 'percentage': 0}
        
        outlier_indices = values.index[outlier_mask].tolist()
        
        return {
            'count': len(outlier_indices),
            'indices': outlier_indices,
            'percentage': (len(outlier_indices) / len(values)) * 100 if len(values) > 0 else 0
        }
    
    @staticmethod
    def validate_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate metric values.
        
        Args:
            metrics: Dictionary of metrics
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'status': 'valid',
            'errors': [],
            'warnings': [],
            'checks': {}
        }
        
        # Check for negative values
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if value < 0 and key not in ['revenue_trend', 'growth']:
                    validation_results['warnings'].append(f"{key} has negative value: {value}")
                    validation_results['checks'][key] = 'warning'
        
        # Check for NaN values
        for key, value in metrics.items():
            if isinstance(value, float) and pd.isna(value):
                validation_results['warnings'].append(f"{key} is NaN")
                validation_results['checks'][key] = 'error'
        
        # Check for unreasonable values
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if key in ['retention_d1', 'retention_d7', 'retention_d30']:
                    if value > 100:
                        validation_results['warnings'].append(f"{key} exceeds 100%: {value}")
                        validation_results['checks'][key] = 'warning'
                elif key in ['quality_score']:
                    if value > 100:
                        validation_results['warnings'].append(f"{key} exceeds 100: {value}")
                        validation_results['checks'][key] = 'warning'
        
        if validation_results['warnings']:
            validation_results['status'] = 'warning'
        
        if validation_results['errors']:
            validation_results['status'] = 'error'
        
        return validation_results
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate DataFrame against schema.
        
        Args:
            df: DataFrame to validate
            schema: Schema definition
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required columns
        required_columns = schema.get('required_columns', [])
        for col in required_columns:
            if col not in df.columns:
                results['valid'] = False
                results['errors'].append(f"Required column missing: {col}")
        
        # Check data types
        dtypes = schema.get('dtypes', {})
        for col, dtype in dtypes.items():
            if col in df.columns:
                try:
                    df[col].astype(dtype)
                except:
                    results['valid'] = False
                    results['errors'].append(f"Column {col} cannot be cast to {dtype}")
        
        return results