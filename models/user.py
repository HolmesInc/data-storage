from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
from .enums import StorageGatewayType


class User(Base):
    """
    User Model - Represents a user account.

    Attrs:
        - id: Unique identifier (primary key)
        - email: User's email (unique)
        - username: User's username (unique)
        - hashed_password: Bcrypt hashed password
        - is_active: Whether the account is active
        - created_at: Timestamp when the account was created
        - datarooms: Relationship to all datarooms owned by this user
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: one User has many DataRooms
    datarooms = relationship("DataRoom", back_populates="owner", cascade="all, delete-orphan")

    # Relationship: one User has many Storage Gateways
    storage_gateways = relationship(
        "StorageGateway",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    @property
    def gateways_by_type(self):
        return {gateway.type: gateway for gateway in self.storage_gateways}

    @property
    def telegram_gateway(self):
        gateway = self.gateways_by_type.get(
            StorageGatewayType.TELEGRAM
        )
        return gateway.telegram_gateway if gateway else None
