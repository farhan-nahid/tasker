"""
Database Configuration and Connection Management.

This module handles all database-related configurations including:
- SQLAlchemy engine setup with PostgreSQL
- Connection pool management
- Session factory configuration
- SSL connection settings for remote databases
- Connection testing and health checks
"""

from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from urllib.parse import quote_plus

from .app_vars import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

# URL encode the password to handle special characters safely
encoded_password = quote_plus(DB_PASS)

# Construct PostgreSQL connection URL for psycopg2 driver
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{encoded_password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create SQLAlchemy engine with optimized settings
engine = create_engine(
    DATABASE_URL,
    # Connection arguments for remote database support
    connect_args={
        "sslmode": "require",  # Force SSL for secure remote connections
        "host": DB_HOST,       # Explicitly set host for TCP connection
        "port": DB_PORT,       # Explicitly set port
    },
    # Connection pool settings
    pool_pre_ping=True,         # Validate connections before use
    pool_recycle=3600,          # Recycle connections every hour
    echo=False                  # Set to True for SQL query logging
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to provide database sessions.
    
    Creates a new database session for each request and ensures
    proper cleanup after the request is completed.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/users/")
        async def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
# Type alias for dependency injection
DbSession = Annotated[Session, Depends(get_db)]


def check_db_connection() -> None:
    """
    Test database connectivity and log connection status.
    
    Performs a simple SELECT 1 query to verify the database
    connection is working properly. Logs success/failure with
    connection timing information.
    
    Raises:
        Exception: If database connection fails
        
    Example:
        try:
            check_db_connection()
            print("Database ready")
        except Exception as e:
            print(f"Database unavailable: {e}")
    """
    try:
        # Import logger here to avoid circular import issues
        from ..logging import logger
        
        import time
        start_time = time.time()
        
        # Test connection with simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            duration = time.time() - start_time
            
            logger.info(
                f"Database connection successful - "
                f"{DB_HOST}:{DB_PORT}/{DB_NAME} "
                f"({round(duration * 1000, 1)}ms)"
            )
            
    except Exception as e:
        # Handle logging import failure gracefully
        try:
            from ..logging import logger
            logger.error(
                f"Database connection failed - "
                f"{DB_HOST}:{DB_PORT}/{DB_NAME} - {str(e)}"
            )
        except ImportError:
            # Fallback to print if logging isn't available
            print(f"Database connection failed: {e}")
            
        # Re-raise the exception for proper error handling
        raise


# Export main components
__all__ = [
    "engine",
    "SessionLocal", 
    "Base",
    "get_db",
    "DbSession",
    "check_db_connection"
]
