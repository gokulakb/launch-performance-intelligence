"""
Database initialization with sample data for the Launch Performance Dashboard.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

def create_database():
    """Create database with sample data."""
    
    # Ensure directory exists
    os.makedirs('database', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('database/launch_performance.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS events")
    cursor.execute("DROP TABLE IF EXISTS revenue")
    cursor.execute("DROP TABLE IF EXISTS retention")
    cursor.execute("DROP TABLE IF EXISTS launch_metrics")
    cursor.execute("DROP TABLE IF EXISTS quality_metrics")
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            company TEXT,
            role TEXT,
            college TEXT,
            signup_date DATETIME,
            last_active DATETIME,
            status TEXT,
            profile_completed INTEGER,
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    
    # Create events table
    cursor.execute('''
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            user_id TEXT,
            event_type TEXT,
            event_name TEXT,
            timestamp DATETIME,
            session_id TEXT,
            page_url TEXT,
            referrer TEXT,
            device_type TEXT,
            browser TEXT,
            os TEXT,
            country TEXT,
            city TEXT,
            duration INTEGER,
            event_metadata TEXT,
            created_at DATETIME
        )
    ''')
    
    # Create revenue table
    cursor.execute('''
        CREATE TABLE revenue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            user_id TEXT,
            company TEXT,
            recruiter TEXT,
            college TEXT,
            amount REAL,
            currency TEXT,
            transaction_date DATE,
            payment_method TEXT,
            status TEXT,
            description TEXT,
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    
    # Create retention table
    cursor.execute('''
        CREATE TABLE retention (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cohort TEXT,
            user_id TEXT,
            company TEXT,
            signup_date DATE,
            day_1_retained INTEGER,
            day_7_retained INTEGER,
            day_30_retained INTEGER,
            week_4_retained INTEGER,
            monthly_retained INTEGER,
            churn_date DATE,
            churned INTEGER,
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    
    # Create launch_metrics table
    cursor.execute('''
        CREATE TABLE launch_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            metric_date DATE,
            visitors INTEGER,
            active_users INTEGER,
            signups INTEGER,
            applications INTEGER,
            interviews INTEGER,
            offers INTEGER,
            hires INTEGER,
            revenue REAL,
            retention_rate REAL,
            quality_score REAL,
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    
    # Create quality_metrics table
    cursor.execute('''
        CREATE TABLE quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            metric_type TEXT,
            table_name TEXT,
            column_name TEXT,
            value REAL,
            sample_size INTEGER,
            total_count INTEGER,
            null_count INTEGER,
            duplicate_count INTEGER,
            anomaly_count INTEGER,
            validation_status TEXT,
            confidence REAL,
            last_refresh DATETIME,
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    
    # Sample data generation
    companies = ['TechCorp', 'DataFlow', 'CloudNine', 'SmartSolutions', 'InnovateLabs']
    recruiters = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Martinez']
    colleges = ['MIT', 'Stanford', 'Harvard', 'Berkeley', 'Caltech', 'Princeton', 'Yale']
    event_types = ['visitor', 'signup', 'profile_complete', 'application', 'interview', 'offer', 'hire']
    statuses = ['active', 'inactive']
    roles = ['Engineer', 'Manager', 'Analyst', 'Director', 'VP']
    devices = ['Desktop', 'Mobile', 'Tablet']
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
    oss = ['Windows', 'Mac', 'Linux', 'iOS', 'Android']
    countries = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'IN']
    cities = ['NYC', 'LA', 'London', 'Berlin', 'Sydney', 'Paris', 'Mumbai']
    payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Wire']
    
    now = datetime.now()
    
    print("Generating users...")
    # Generate users
    users = []
    for i in range(500):
        company = random.choice(companies)
        signup_date = now - timedelta(days=random.randint(1, 365))
        last_active = signup_date + timedelta(days=random.randint(0, 30))
        
        # Use random.choices() for weighted random
        status = random.choices(statuses, weights=[0.7, 0.3])[0]
        
        users.append((
            f'user_{i:04d}',
            f'User {i}',
            f'user{i}@example.com',
            f'+1{random.randint(1000000000, 9999999999)}',
            company,
            random.choice(roles),
            random.choice(colleges),
            signup_date.strftime('%Y-%m-%d %H:%M:%S'),
            last_active.strftime('%Y-%m-%d %H:%M:%S'),
            status,
            random.randint(0, 1),
            now.strftime('%Y-%m-%d %H:%M:%S'),
            now.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    cursor.executemany('''
        INSERT INTO users 
        (user_id, name, email, phone, company, role, college, signup_date, last_active, status, profile_completed, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)
    print(f"  ✅ Added {len(users)} users")
    
    print("Generating events...")
    # Generate events
    events = []
    for i in range(2000):
        user_idx = random.randint(0, 499)
        event_type = random.choice(event_types)
        event_date = now - timedelta(days=random.randint(0, 90))
        
        events.append((
            f'evt_{i:05d}',
            f'user_{user_idx:04d}',
            event_type,
            f'{event_type}_event',
            event_date.strftime('%Y-%m-%d %H:%M:%S'),
            f'session_{random.randint(1, 1000)}',
            f'/page/{random.randint(1, 20)}',
            f'referrer_{random.randint(1, 5)}.com',
            random.choice(devices),
            random.choice(browsers),
            random.choice(oss),
            random.choice(countries),
            random.choice(cities),
            random.randint(10, 600),
            '{}',
            now.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    cursor.executemany('''
        INSERT INTO events 
        (event_id, user_id, event_type, event_name, timestamp, session_id, page_url, referrer, device_type, browser, os, country, city, duration, event_metadata, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', events)
    print(f"  ✅ Added {len(events)} events")
    
    print("Generating revenue...")
    # Generate revenue
    revenue = []
    for i in range(300):
        user_idx = random.randint(0, 499)
        company = random.choice(companies)
        trans_date = now - timedelta(days=random.randint(0, 90))
        
        revenue.append((
            f'trans_{i:06d}',
            f'user_{user_idx:04d}',
            company,
            random.choice(recruiters),
            random.choice(colleges),
            random.randint(500, 15000),
            'USD',
            trans_date.strftime('%Y-%m-%d'),
            random.choice(payment_methods),
            'completed',
            f'Transaction {i}',
            now.strftime('%Y-%m-%d %H:%M:%S'),
            now.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    cursor.executemany('''
        INSERT INTO revenue 
        (transaction_id, user_id, company, recruiter, college, amount, currency, transaction_date, payment_method, status, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', revenue)
    print(f"  ✅ Added {len(revenue)} revenue transactions")
    
    print("Generating retention data...")
    # Generate retention data
    retention = []
    for i in range(500):
        user_idx = i
        signup_date = now - timedelta(days=random.randint(1, 365))
        cohort = signup_date.strftime('%Y-%m')
        
        # Determine retention based on signup date (older users have lower retention)
        days_old = (now - signup_date).days
        retention_prob = max(0.1, 1 - (days_old / 365) * 0.5)
        
        # Random retention values based on probability
        day_1 = random.randint(0, 1)
        day_7 = random.randint(0, 1) if random.random() < retention_prob else 0
        day_30 = random.randint(0, 1) if random.random() < retention_prob * 0.8 else 0
        week_4 = random.randint(0, 1) if random.random() < retention_prob * 0.7 else 0
        monthly = random.randint(0, 1) if random.random() < retention_prob * 0.6 else 0
        churned = random.randint(0, 1) if random.random() > retention_prob else 0
        
        retention.append((
            cohort,
            f'user_{user_idx:04d}',
            random.choice(companies),
            signup_date.strftime('%Y-%m-%d'),
            day_1,
            day_7,
            day_30,
            week_4,
            monthly,
            None if not churned else (signup_date + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
            churned,
            now.strftime('%Y-%m-%d %H:%M:%S'),
            now.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    cursor.executemany('''
        INSERT INTO retention 
        (cohort, user_id, company, signup_date, day_1_retained, day_7_retained, day_30_retained, week_4_retained, monthly_retained, churn_date, churned, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', retention)
    print(f"  ✅ Added {len(retention)} retention records")
    
    print("Generating launch metrics...")
    # Generate launch metrics - now generating data up to today
    launch_metrics = []
    for days_ago in range(90, -1, -1):
        date = now - timedelta(days=days_ago)
        date_str = date.strftime('%Y-%m-%d')
        
        for company in companies:
            # Base values with realistic distributions
            base_visitors = random.randint(100, 500)
            base_active = int(base_visitors * random.uniform(0.3, 0.7))
            base_signups = int(base_visitors * random.uniform(0.05, 0.15))
            base_applications = int(base_signups * random.uniform(0.3, 0.6))
            base_interviews = int(base_applications * random.uniform(0.3, 0.5))
            base_offers = int(base_interviews * random.uniform(0.2, 0.4))
            base_hires = int(base_offers * random.uniform(0.3, 0.5))
            base_revenue = random.randint(1000, 10000)
            base_retention = random.uniform(0.3, 0.8)
            base_quality = random.uniform(0.7, 0.95)
            
            # Add some trend (improving over time)
            days_from_start = days_ago / 90
            trend_factor = 1 + (1 - days_from_start) * 0.5
            
            # Add some weekly seasonality
            day_of_week = date.weekday()
            seasonal_factor = 1 + 0.2 * (1 - abs(day_of_week - 3) / 3)  # Higher mid-week
            
            final_factor = trend_factor * seasonal_factor
            
            launch_metrics.append((
                company,
                date_str,
                int(base_visitors * final_factor),
                int(base_active * final_factor),
                int(base_signups * final_factor),
                int(base_applications * final_factor),
                int(base_interviews * final_factor),
                int(base_offers * final_factor),
                int(base_hires * final_factor),
                base_revenue * final_factor,
                min(1, base_retention * (0.8 + 0.2 * final_factor)),
                min(1, base_quality * (0.85 + 0.15 * final_factor)),
                now.strftime('%Y-%m-%d %H:%M:%S'),
                now.strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    cursor.executemany('''
        INSERT INTO launch_metrics 
        (company, metric_date, visitors, active_users, signups, applications, interviews, offers, hires, revenue, retention_rate, quality_score, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', launch_metrics)
    print(f"  ✅ Added {len(launch_metrics)} launch metrics")
    
    print("Generating quality metrics...")
    # Generate quality metrics
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    quality_metrics = [
        ('users_completeness', 'completeness', 'users', 'all', 0.94, 500, 500, 30, 5, 2, 'warning', 0.95, now_str, now_str, now_str),
        ('events_completeness', 'completeness', 'events', 'all', 0.96, 2000, 2000, 80, 10, 5, 'valid', 0.97, now_str, now_str, now_str),
        ('revenue_completeness', 'completeness', 'revenue', 'all', 0.98, 300, 300, 6, 2, 0, 'valid', 0.99, now_str, now_str, now_str),
        ('users_consistency', 'consistency', 'users', 'email', 0.92, 500, 500, 0, 0, 40, 'warning', 0.93, now_str, now_str, now_str),
        ('users_accuracy', 'accuracy', 'users', 'phone', 0.89, 500, 500, 0, 0, 55, 'warning', 0.91, now_str, now_str, now_str),
        ('overall_quality', 'overall', 'all', 'all', 0.91, 3300, 3300, 116, 17, 102, 'valid', 0.95, now_str, now_str, now_str),
    ]
    
    cursor.executemany('''
        INSERT INTO quality_metrics 
        (metric_name, metric_type, table_name, column_name, value, sample_size, total_count, null_count, duplicate_count, anomaly_count, validation_status, confidence, last_refresh, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', quality_metrics)
    print(f"  ✅ Added {len(quality_metrics)} quality metrics")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ Database created successfully with sample data!")
    print("="*50)
    print(f"   - 500 users")
    print(f"   - 2,000 events")
    print(f"   - 300 revenue transactions")
    print(f"   - 500 retention records")
    print(f"   - 91 days of launch metrics (up to today)")
    print(f"   - 6 quality metrics")
    print("="*50)
    print("\n🚀 You can now run: streamlit run app.py")

if __name__ == "__main__":
    create_database()