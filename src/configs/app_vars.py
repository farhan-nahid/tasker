import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Database Configuration
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_NAME: str = os.getenv("DB_NAME", "tasker")
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASS: str = os.getenv("DB_PASSWORD", "password")
DB_PORT: int = int(os.getenv("DB_PORT", "5432"))

# Application Configuration
PORT: int = int(os.getenv("PORT", "8000"))