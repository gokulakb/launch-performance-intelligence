"""
Configuration settings for the Launch Performance Intelligence Dashboard.
Contains all constants, paths, and configuration parameters.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
ASSETS_DIR = BASE_DIR / "assets"

# Database configuration
DATABASE_PATH = DATABASE_DIR / "launch_performance.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Data files
DATA_FILES = {
    "users": DATA_DIR / "users.csv",
    "events": DATA_DIR / "events.csv",
    "revenue": DATA_DIR / "revenue.csv",
    "retention": DATA_DIR / "retention.csv",
    "quality": DATA_DIR / "quality.csv",
    "launch_metrics": DATA_DIR / "launch_metrics.csv"
}

# Company configuration
COMPANIES = ["TechCorp", "DataFlow", "CloudNine", "SmartSolutions", "InnovateLabs"]
RECRUITERS = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Martinez"]
COLLEGES = ["MIT", "Stanford", "Harvard", "Berkeley", "Caltech"]

# Metric thresholds
QUALITY_THRESHOLDS = {
    "completeness": 0.95,
    "consistency": 0.90,
    "accuracy": 0.95
}

# KPI definitions
KPIS = {
    "visitors": {"label": "Visitors", "format": "{:,}", "icon": "👥"},
    "active_users": {"label": "Active Users", "format": "{:,}", "icon": "🟢"},
    "signups": {"label": "Signups", "format": "{:,}", "icon": "📝"},
    "applications": {"label": "Applications", "format": "{:,}", "icon": "📄"},
    "interviews": {"label": "Interviews", "format": "{:,}", "icon": "🎯"},
    "offers": {"label": "Offers", "format": "{:,}", "icon": "🏆"},
    "hires": {"label": "Hires", "format": "{:,}", "icon": "✅"},
    "revenue": {"label": "Revenue", "format": "${:,.0f}", "icon": "💰"},
    "retention": {"label": "Retention", "format": "{:.1%}", "icon": "🔄"},
    "quality_score": {"label": "Quality Score", "format": "{:.1f}", "icon": "⭐"}
}

# Color palette for dashboard
COLORS = {
    "primary": "#1E88E5",
    "secondary": "#FF6B6B",
    "success": "#4CAF50",
    "warning": "#FFA726",
    "danger": "#E53935",
    "info": "#26C6DA",
    "light": "#F5F5F5",
    "dark": "#263238",
    "gradient": ["#1E88E5", "#4CAF50", "#FFA726", "#E53935"],
    "palette": [
        "#1E88E5", "#FF6B6B", "#4CAF50", "#FFA726", "#26C6DA",
        "#8E24AA", "#FF5722", "#00BCD4", "#FF4081", "#7CB342"
    ]
}

# SQL queries configuration
QUERY_CONFIG = {
    "max_rows": 10000,
    "cache_timeout": 300  # seconds
}

# Export configuration
EXPORT_CONFIG = {
    "csv_delimiter": ",",
    "excel_engine": "openpyxl",
    "pdf_orientation": "landscape"
}

# Machine learning configuration
ML_CONFIG = {
    "forecast_periods": 30,  # days
    "test_size": 0.2,
    "random_state": 42
}

# Dashboard settings
DASHBOARD_CONFIG = {
    "title": "Launch Performance Intelligence Dashboard",
    "page_title": "Launch Intelligence",
    "page_icon": "📊",
    "layout": "wide",
    "sidebar_state": "expanded"
}

# Date ranges
DATE_RANGES = {
    "last_7_days": 7,
    "last_30_days": 30,
    "last_90_days": 90,
    "last_365_days": 365
}

def get_env_var(key: str, default: str = None) -> str:
    """Get environment variable with default fallback."""
    return os.getenv(key, default)

# Database settings
DB_SETTINGS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600
}