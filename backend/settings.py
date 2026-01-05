import os
import logging
from typing import List

# -------------------------------------------------------------------------------------------------------------------
# DATABASE SETTINGS
# -------------------------------------------------------------------------------------------------------------------
# PostgreSQL connection string
# Format: postgresql://user:password@host:port/database
DB_HOST = "localhost"
DB_PORT = 5400
DB_NAME = "dataroom_db"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://postgres:postgres@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# -------------------------------------------------------------------------------------------------------------------
# AUTHENTICATION SETTINGS
# -------------------------------------------------------------------------------------------------------------------
# JWT Secret key - change this to a strong random string in production
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "your-secret-key-change-this-in-production-use-strong-random-string"
)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# JWT configuration
JWT_ALGORITHM = "HS256"

# -------------------------------------------------------------------------------------------------------------------
# API SETTINGS
# -------------------------------------------------------------------------------------------------------------------
API_TITLE = "Data Room API"
API_DESCRIPTION = "API for managing data rooms, folders, and files"
API_VERSION = "1.0.0"

# API Documentation URLs
API_DOCS_URL = "/api/docs"
API_REDOC_URL = "/api/redoc"
API_OPENAPI_URL = "/api/openapi.json"

# -------------------------------------------------------------------------------------------------------------------
# CORS SETTINGS
# -------------------------------------------------------------------------------------------------------------------
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5001",
    "http://127.0.0.1:5001",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# -------------------------------------------------------------------------------------------------------------------
# FILE UPLOAD SETTINGS
# -------------------------------------------------------------------------------------------------------------------
UPLOADS_DIRECTORY = "uploads"

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOADS_DIRECTORY):
    os.makedirs(UPLOADS_DIRECTORY)


# -------------------------------------------------------------------------------------------------------------------
# PROJECT SETTINGS
# -------------------------------------------------------------------------------------------------------------------
class CustomPathFilter(logging.Filter):
    """
    Format a path to an origin file printed a log to leave only relative path instead of absolute path
    """
    def filter(self, record):
        # set the project's base directory
        project_dir = os.path.abspath(os.path.dirname(__file__))
        # modify pathname to be relative
        record.pathname = os.path.relpath(record.pathname, project_dir)
        return True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "custom_path_filter": {
            "()": CustomPathFilter,
        },
    },
    "formatters": {
        "common": {
            "format": "[{name}:{levelname} {asctime}] ({module}|{pathname}|{lineno}): {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "common",
            "filters": ["custom_path_filter"],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
