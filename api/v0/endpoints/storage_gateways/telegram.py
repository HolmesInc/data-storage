from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db
from models.user import User
from models.storage_gateway import TelegramGateway, StorageGateway
from api.dependencies import get_current_user
from api.v0.schemas.storage_gateways import telegram as telegram_schema

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("", response_model=telegram_schema.CreateTelegramGatewayResponse)
def register(
        chat_data: telegram_schema.CreateTelegramGateway,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Register a Telegram gateway to store user data.
    """
    # Check if storage gateway already exists
    existing_storage_gateway = db.query(StorageGateway).filter(StorageGateway.owner_id == current_user.id).first()
    # if not existing_storage_gateway:

# # Check if username already exists
# existing_username = db.query(User).filter(User.username == user_data.username).first()
# if existing_username:
#     raise HTTPException(
#         status_code=status.HTTP_400_BAD_REQUEST,
#         detail="Username already taken"
#     )
#
# # Create new user with hashed password
# hashed_password = hash_password(user_data.password)
# new_user = User(
#     email=user_data.email,
#     username=user_data.username,
#     hashed_password=hashed_password
# )
#
# db.add(new_user)
# db.commit()
# db.refresh(new_user)
#
# return new_user


@router.get("", response_model=telegram_schema.GetTelegramGateway)
def retreive(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get a Telegram gateway data of a user.
    """
    if not current_user.telegram_gateway:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Telegram gateway found for the user"
        )

    return

@router.put("", response_model=telegram_schema.UpdateTelegramGatewayResponse)
def retreive(
        chat_data: telegram_schema.UpdateTelegramGateway,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Update a Telegram gateway data of a user.
    """

    return
