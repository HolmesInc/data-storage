"""
Main API Router Module

This module serves as the entry point for all API versions.
It organizes and includes routers from different API versions.

Structure:
- api/
  - __init__.py
  - router.py (this file - main entry point)
  - v0/
    - __init__.py
    - router.py (v0 main router)
    - endpoints/
      - dataroom.py
      - folder.py
      - file.py
"""

from fastapi import APIRouter
from .v0.router import router as v0_router

# Create the main API router that will be included in the main app
api_router = APIRouter(prefix="/api")
api_router.include_router(v0_router, prefix="/v0")
