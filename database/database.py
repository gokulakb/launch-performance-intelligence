"""
Database management and operations for the Launch Performance Intelligence Dashboard.
Handles connection, initialization, and CRUD operations.
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
import os

from config import DATABASE_URL, DATABASE_DIR, DB_SETTINGS
from database.schema import Base, create_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Singleton database manager with connection pooling and session handling."""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database engine and session factory."""
        try:
            # Ensure database directory exists
            DATABASE_DIR.mkdir(parents=True, exist_ok=True)
            
            # Create engine with connection pooling
            self._engine = create_engine(
                DATABASE_URL,
                echo=False,
                pool_size=DB_SETTINGS['pool_size'],
                max_overflow=DB_SETTINGS['max_overflow'],
                pool_timeout=DB_SETTINGS['pool_timeout'],
                pool_recycle=DB_SETTINGS['pool_recycle'],
                connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
            )
            
            # Create session factory
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Create tables if they don't exist
            create_schema(self._engine)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get a database session with context management."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: dict = None):
        """Execute a raw SQL query and return results as pandas DataFrame."""
        with self.get_session() as session:
            try:
                result = session.execute(text(query), params or {})
                return pd.DataFrame(result.fetchall())
            except Exception as e:
                logger.error(f"Query execution error: {e}")
                raise
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        """Insert a pandas DataFrame into a table."""
        with self.get_session() as session:
            try:
                df.to_sql(
                    table_name,
                    session.bind,
                    if_exists=if_exists,
                    index=False,
                    method='multi'
                )
                logger.info(f"Inserted {len(df)} rows into {table_name}")
            except Exception as e:
                logger.error(f"Error inserting data: {e}")
                raise
    
    def get_table_info(self, table_name: str):
        """Get information about a table."""
        inspector = inspect(self._engine)
        return {
            'columns': inspector.get_columns(table_name),
            'primary_keys': inspector.get_pk_constraint(table_name),
            'foreign_keys': inspector.get_foreign_keys(table_name),
            'indexes': inspector.get_indexes(table_name)
        }
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        inspector = inspect(self._engine)
        return table_name in inspector.get_table_names()
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table."""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return int(result['count'].iloc[0]) if not result.empty else 0
    
    def clear_table(self, table_name: str):
        """Delete all rows from a table."""
        with self.get_session() as session:
            try:
                session.execute(text(f"DELETE FROM {table_name}"))
                logger.info(f"Cleared table {table_name}")
            except Exception as e:
                logger.error(f"Error clearing table {table_name}: {e}")
                raise
    
    def backup_database(self, backup_path: str = None):
        """Create a backup of the database."""
        if backup_path is None:
            backup_path = DATABASE_DIR / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        try:
            with self.get_session() as session:
                session.execute(text(f"VACUUM INTO '{backup_path}'"))
            logger.info(f"Database backup created at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    def initialize_database(self):
        """Initialize database with sample data from CSV files."""
        try:
            # Import data from CSV files
            from config import DATA_FILES
            
            for table_name, file_path in DATA_FILES.items():
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    self.insert_dataframe(df, table_name, if_exists='replace')
                    logger.info(f"Imported {len(df)} rows from {file_path.name}")
            
            # Update quality metrics
            self._update_quality_metrics()
            
            logger.info("Database initialization complete")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _update_quality_metrics(self):
        """Update quality metrics for all tables."""
        from database.queries import Queries
        queries = Queries()
        
        # Get all tables
        inspector = inspect(self._engine)
        tables = inspector.get_table_names()
        
        for table in tables:
            # Calculate completeness
            completeness = queries.get_table_completeness(table)
            if completeness:
                self.insert_dataframe(
                    pd.DataFrame([completeness]),
                    'quality_metrics',
                    if_exists='append'
                )
    
    @property
    def engine(self):
        """Get the database engine."""
        return self._engine

# Singleton instance
db = Database()