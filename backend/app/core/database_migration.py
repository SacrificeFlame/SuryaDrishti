"""
Database Migration Support
Supports both SQLite (development) and PostgreSQL (production)
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """
    Get database URL from environment or config.
    Supports both SQLite and PostgreSQL.
    """
    # Check for PostgreSQL connection string first
    postgres_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    
    if postgres_url:
        # Ensure it's a valid PostgreSQL URL
        if not postgres_url.startswith('postgresql://') and not postgres_url.startswith('postgresql+psycopg2://'):
            # Try to convert common formats
            if postgres_url.startswith('postgres://'):
                postgres_url = postgres_url.replace('postgres://', 'postgresql://', 1)
            else:
                logger.warning(f"Invalid PostgreSQL URL format: {postgres_url}")
                postgres_url = None
    
    if postgres_url:
        logger.info("Using PostgreSQL database")
        return postgres_url
    
    # Fall back to SQLite
    sqlite_path = os.getenv('SQLITE_DB_PATH', 'suryादrishti.db')
    logger.info(f"Using SQLite database: {sqlite_path}")
    return f"sqlite:///{sqlite_path}"


def create_database_engine():
    """Create database engine with appropriate driver"""
    database_url = get_database_url()
    
    if database_url.startswith('postgresql'):
        # PostgreSQL - use asyncpg or psycopg2
        try:
            # Try asyncpg first (faster for async operations)
            if 'asyncpg' not in database_url:
                database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        except:
            # Fall back to psycopg2
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://', 1)
        
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,
            max_overflow=20
        )
    else:
        # SQLite
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}  # SQLite-specific
        )
    
    return engine


def migrate_to_postgresql(source_db_path: str, target_postgres_url: str):
    """
    Migrate data from SQLite to PostgreSQL.
    
    Args:
        source_db_path: Path to SQLite database file
        target_postgres_url: PostgreSQL connection URL
    """
    logger.info(f"Starting migration from SQLite ({source_db_path}) to PostgreSQL")
    
    # Create engines
    sqlite_engine = create_engine(f"sqlite:///{source_db_path}")
    postgres_engine = create_engine(target_postgres_url)
    
    # Get table names
    with sqlite_engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
    
    logger.info(f"Found {len(tables)} tables to migrate: {tables}")
    
    # Create tables in PostgreSQL (using existing models)
    from app.models.database import Base
    Base.metadata.create_all(postgres_engine)
    
    # Migrate data
    for table_name in tables:
        if table_name == 'sqlite_sequence':
            continue
        
        logger.info(f"Migrating table: {table_name}")
        
        with sqlite_engine.connect() as sqlite_conn:
            # Get all data from SQLite
            result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            columns = result.keys()
        
        if rows:
            # Insert into PostgreSQL
            with postgres_engine.connect() as postgres_conn:
                for row in rows:
                    values = dict(zip(columns, row))
                    # Build INSERT statement
                    columns_str = ', '.join(columns)
                    placeholders = ', '.join([f':{col}' for col in columns])
                    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    
                    try:
                        postgres_conn.execute(text(insert_sql), values)
                    except Exception as e:
                        logger.warning(f"Failed to insert row into {table_name}: {e}")
                
                postgres_conn.commit()
            
            logger.info(f"Migrated {len(rows)} rows from {table_name}")
    
    logger.info("Migration completed successfully")


def check_database_connection():
    """Check if database connection is working"""
    try:
        engine = create_database_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False





