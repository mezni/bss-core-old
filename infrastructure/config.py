import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{Path(__file__).parent.parent.parent}/data/bss_core.db"
)

# API configuration
API_V1_STR = "/api/v1"
PROJECT_NAME = "BSS-Core Shipment Management"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# CORS
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS",
    "http://localhost,http://localhost:8080,http://127.0.0.1:8080",
).split(",")