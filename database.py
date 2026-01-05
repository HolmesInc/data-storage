"""
Database Configuration Module

This module handles all database-related setup for the FastAPI application.
It uses SQLAlchemy as the ORM (Object-Relational Mapping) tool.

What is happening here:
- We import SQLAlchemy's create_engine to manage database connections
- We create a database URL that points to a PostgreSQL database
- SessionLocal creates database sessions for each request
- Base is the declarative base class that all our models inherit from
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_URL

# Create the database engine
# For PostgreSQL, we use connect_args to set connection timeout
engine = create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": 10} if "postgresql" in DATABASE_URL else {},
    pool_pre_ping=True,  # Verify connections before using them
)

# SessionLocal factory creates new database sessions
# Each request will get its own session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the declarative base class
# All our database models (DataRoom, Folder, File) will inherit from this
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session to route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
