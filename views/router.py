from fastapi import APIRouter
from .v0 import (
    auth,
    index,
    user_settings,
)

html_router = APIRouter(prefix="", tags=["html"])

html_router.include_router(index.router)
html_router.include_router(auth.router)
html_router.include_router(user_settings.router)