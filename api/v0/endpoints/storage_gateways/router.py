from fastapi import APIRouter
from . import telegram

router = APIRouter(prefix="/storage-gateways", tags=["storage-gateways"])

router.include_router(telegram.router)
