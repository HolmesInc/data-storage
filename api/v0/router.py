"""
API v0 Router Module

This module is the main router for API version 0.
Include individual resource routers.
Each resource router handles its own resource endpoints, for example:
 - auth: /auth/register, /auth/login
 - dataroom: /datarooms, /datarooms/{id}, etc.
 - folder: /folders, /folders/{id}, etc.
 - file: /files, /files/{id}, etc.
"""

from fastapi import APIRouter
from .endpoints import (
    auth,
    dataroom,
    folder,
    file
)

# This router will have /api/v0 prefix added by the main api router
router = APIRouter(tags=["v0"])

router.include_router(auth.router, tags=["auth"])
router.include_router(dataroom.router, tags=["dataroom"])
router.include_router(folder.router, tags=["folder"])
router.include_router(file.router, tags=["file"])
