"""
Database schema definitions for the Launch Performance Intelligence Dashboard.
Defines all tables, relationships, and constraints.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    Date, Boolean, ForeignKey, Text, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    """Users table storing user information."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    company = Column(String(100), nullable=False, index=True)
    role = Column(String(50))
    college = Column(String(100))
    signup_date = Column(DateTime, nullable=False)
    last_active = Column(DateTime)
    status = Column(String(20), default='active')
    profile_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    events = relationship("Event", back_populates="user")
    revenue = relationship("Revenue", back_populates="user")
    
    __table_args__ = (
        Index('idx_user_company', 'company'),
        Index('idx_user_signup', 'signup_date'),
    )

class Event(Base):
    """Events table tracking user activities."""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_name = Column(String(100))
    timestamp = Column(DateTime, nullable=False, index=True)
    session_id = Column(String(50))
    page_url = Column(String(200))
    referrer = Column(String(200))
    device_type = Column(String(20))
    browser = Column(String(20))
    os = Column(String(20))
    country = Column(String(50))
    city = Column(String(50))
    duration = Column(Integer)  # in seconds
    metadata = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="events")
    
    __table_args__ = (
        Index('idx_event_user_time', 'user_id', 'timestamp'),
        Index('idx_event_type_time', 'event_type', 'timestamp'),
    )

class Revenue(Base):
    """Revenue transactions table."""
    __tablename__ = 'revenue'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    company = Column(String(100), nullable=False, index=True)
    recruiter = Column(String(100), nullable=False, index=True)
    college = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    transaction_date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(50))
    status = Column(String(20), default='completed')
    description = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="revenue")
    
    __table_args__ = (
        Index('idx_revenue_company_date', 'company', 'transaction_date'),
        Index('idx_revenue_recruiter', 'recruiter'),
        Index('idx_revenue_college', 'college'),
    )

class Retention(Base):
    """User retention tracking table."""
    __tablename__ = 'retention'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cohort = Column(String(20), nullable=False, index=True)  # YYYY-MM
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    company = Column(String(100), nullable=False, index=True)
    signup_date = Column(Date, nullable=False)
    day_1_retained = Column(Boolean, default=False)
    day_7_retained = Column(Boolean, default=False)
    day_30_retained = Column(Boolean, default=False)
    week_4_retained = Column(Boolean, default=False)
    monthly_retained = Column(Boolean, default=False)
    churn_date = Column(Date)
    churned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('cohort', 'user_id', name='uq_retention_user_cohort'),
        Index('idx_retention_cohort', 'cohort'),
        Index('idx_retention_company', 'company'),
    )

class QualityMetric(Base):
    """Data quality metrics table."""
    __tablename__ = 'quality_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(50), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # completeness, consistency, accuracy
    table_name = Column(String(50), nullable=False)
    column_name = Column(String(50))
    value = Column(Float, nullable=False)
    sample_size = Column(Integer)
    total_count = Column(Integer)
    null_count = Column(Integer)
    duplicate_count = Column(Integer)
    anomaly_count = Column(Integer)
    validation_status = Column(String(20), default='valid')
    confidence = Column(Float, default=0.95)
    last_refresh = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    __table_args__ = (
        Index('idx_quality_metric', 'metric_name', 'table_name'),
    )

class LaunchMetric(Base):
    """Overall launch performance metrics."""
    __tablename__ = 'launch_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String(100), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    visitors = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    signups = Column(Integer, default=0)
    applications = Column(Integer, default=0)
    interviews = Column(Integer, default=0)
    offers = Column(Integer, default=0)
    hires = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    retention_rate = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('company', 'metric_date', name='uq_company_metric_date'),
        Index('idx_launch_company_date', 'company', 'metric_date'),
    )

def create_schema(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(engine)