from typing import Annotated, Generator, Optional, Tuple
from fastapi import Depends
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from urllib.parse import quote_plus

from ..utils.logging import logger

from .app_vars import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

# URL encode the password to handle special characters safely
encoded_password = quote_plus(DB_PASS)

# Construct PostgreSQL connection URL for psycopg2 driver
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with optimized settings
engine = create_engine(
    DATABASE_URL,
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


def check_db_connection() -> Tuple[bool, Optional[float], Optional[str]]:
    start_time = time.time()

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            duration_ms = round((time.time() - start_time) * 1000, 1)

            logger.info("Database connected successfully!!")

            return True, duration_ms, None

    except Exception as e:
        error_msg = str(e)

        try:
            logger.error(f"Database connection failed - {error_msg}")
        except Exception:
            print(f"Database connection failed: {error_msg}")

        return False, None, error_msg