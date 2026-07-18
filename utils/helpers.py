"""
General helper utilities for the dashboard.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import json
import hashlib
import re

class Helpers:
    """Collection of general helper functions."""
    
    @staticmethod
    def format_currency(value: float, currency: str = "$") -> str:
        """Format value as currency."""
        if pd.isna(value):
            return f"{currency}0"
        return f"{currency}{value:,.0f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format value as percentage."""
        if pd.isna(value):
            return "0.0%"
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_number(value: float) -> str:
        """Format number with commas."""
        if pd.isna(value):
            return "0"
        return f"{value:,.0f}"
    
    @staticmethod
    def format_date(date_str: Union[str, datetime], format_str: str = "%Y-%m-%d") -> str:
        """Format date string."""
        if isinstance(date_str, datetime):
            return date_str.strftime(format_str)
        try:
            dt = pd.to_datetime(date_str)
            return dt.strftime(format_str)
        except:
            return str(date_str)
    
    @staticmethod
    def safe_divide(a: float, b: float, default: float = 0) -> float:
        """Safe division with fallback."""
        try:
            if b == 0:
                return default
            return a / b
        except:
            return default
    
    @staticmethod
    def safe_mean(values: List[float]) -> float:
        """Safe mean calculation."""
        if not values:
            return 0
        try:
            return np.mean(values)
        except:
            return 0
    
    @staticmethod
    def safe_std(values: List[float]) -> float:
        """Safe standard deviation calculation."""
        if not values:
            return 0
        try:
            return np.std(values)
        except:
            return 0
    
    @staticmethod
    def safe_sum(values: List[float]) -> float:
        """Safe sum calculation."""
        if not values:
            return 0
        try:
            return sum(values)
        except:
            return 0
    
    @staticmethod
    def safe_max(values: List[float]) -> float:
        """Safe max calculation."""
        if not values:
            return 0
        try:
            return max(values)
        except:
            return 0
    
    @staticmethod
    def safe_min(values: List[float]) -> float:
        """Safe min calculation."""
        if not values:
            return 0
        try:
            return min(values)
        except:
            return 0
    
    @staticmethod
    def calculate_trend(values: List[float], lookback: int = 5) -> float:
        """
        Calculate trend direction.
        
        Args:
            values: List of values
            lookback: Number of periods to look back
        
        Returns:
            Trend direction (-1, 0, 1)
        """
        if len(values) < lookback:
            return 0
        
        recent = values[-lookback:]
        trend = np.polyfit(range(len(recent)), recent, 1)[0]
        
        if trend > 0.1:
            return 1
        elif trend < -0.1:
            return -1
        else:
            return 0
    
    @staticmethod
    def generate_id(prefix: str = "") -> str:
        """Generate a unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]
        return f"{prefix}_{timestamp}_{random_part}"
    
    @staticmethod
    def safe_json_loads(json_str: str) -> Dict[str, Any]:
        """Safely load JSON string."""
        try:
            return json.loads(json_str)
        except:
            return {}
    
    @staticmethod
    def safe_json_dumps(data: Dict[str, Any]) -> str:
        """Safely dump JSON."""
        try:
            return json.dumps(data)
        except:
            return "{}"
    
    @staticmethod
    def clean_string(text: str) -> str:
        """Clean a string by removing special characters."""
        if not text:
            return ""
        return re.sub(r'[^\w\s-]', '', text).strip()
    
    @staticmethod
    def truncate_string(text: str, max_length: int = 100) -> str:
        """Truncate string to max length."""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def get_date_range(days: int) -> tuple:
        """Get date range for the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def convert_to_dataframe(data: Union[Dict, List, pd.DataFrame]) -> pd.DataFrame:
        """Convert data to DataFrame."""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        elif isinstance(data, list):
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ""
    
    @staticmethod
    def is_valid_filename(filename: str) -> bool:
        """Check if filename is valid."""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return not any(char in filename for char in invalid_chars)