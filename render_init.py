import os
import sqlite3

def init_database():
    print("Initializing database on Render...")
    os.makedirs('database', exist_ok=True)
    
    try:
        import init_db
        init_db.create_database()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error: {e}")
        create_fallback()

def create_fallback():
    conn = sqlite3.connect('database/launch_performance.db')
    conn.execute('''
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
            quality_score REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("Fallback database created")

if __name__ == "__main__":
    init_database()
