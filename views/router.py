from fastapi import APIRouter
from .v0 import (
    auth,
    index,
)

html_router = APIRouter(prefix="", tags=["html"])

html_router.include_router(auth.router)
html_router.include_router(index.router)
