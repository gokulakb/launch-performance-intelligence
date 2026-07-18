"""
Render.com initialization script for Launch Performance Intelligence Dashboard.
Runs automatically on deployment.
"""

import sqlite3
import os
import sys
import subprocess
from pathlib import Path

def init_database():
    """Initialize the database for Render deployment."""
    
    print("🚀 Starting Render initialization...")
    
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    # Check if database already exists
    db_path = 'database/launch_performance.db'
    
    if os.path.exists(db_path):
        print(f"✅ Database already exists at {db_path}")
        return
    
    print("📦 Creating database with sample data...")
    
    # Run init_db.py
    try:
        # Import and run the initialization
        import init_db
        init_db.create_database()
        print("✅ Database initialized successfully on Render!")
    except ImportError as e:
        print(f"⚠️  init_db.py not found, creating fallback database...")
        create_fallback_database()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        create_fallback_database()

def create_fallback_database():
    """Create a minimal database if init_db fails."""
    try:
        conn = sqlite3.connect('database/launch_performance.db')
        cursor = conn.cursor()
        
        # Create minimal tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS launch_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                metric_date DATE,
                visitors INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                signups INTEGER DEFAULT 0,
                applications INTEGER DEFAULT 0,
                interviews INTEGER DEFAULT 0,
                offers INTEGER DEFAULT 0,
                hires INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0,
                retention_rate REAL DEFAULT 0,
                quality_score REAL DEFAULT 0,
                created_at DATETIME,
                updated_at DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
        
        conn.commit()
        conn.close()
        print("✅ Fallback database created successfully!")
    except Exception as e:
        print(f"❌ Error creating fallback database: {e}")

if __name__ == "__main__":
    init_database()
