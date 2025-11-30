from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from urllib.parse import quote_plus


from .app_vars import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

# URL encode the password to handle special characters
encoded_password = quote_plus(DB_PASS)

# Use postgresql+psycopg2 for psycopg2-binary
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine with SSL and connection parameters for remote database
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",  # Force SSL for remote connections
        "host": DB_HOST,       # Explicitly set host to force TCP connection
        "port": DB_PORT,       # Explicitly set port
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
DbSession = Annotated[Session, Depends(get_db)]
