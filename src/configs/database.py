from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from urllib.parse import quote_plus

from ..utils.logging import logger

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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
# Type alias for dependency injection
DbSession = Annotated[Session, Depends(get_db)]


def check_db_connection() -> None:
    try:
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
            logger.error(
                f"Database connection failed - "
                f"{DB_HOST}:{DB_PORT}/{DB_NAME} - {str(e)}"
            )
        except ImportError:
            # Fallback to print if logging isn't available
            print(f"Database connection failed: {e}")
            
        # Re-raise the exception for proper error handling
        raise
