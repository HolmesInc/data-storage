from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, UniqueConstraint, String
from sqlalchemy.orm import relationship, validates
from database import Base
from .enums import StorageGatewayType


class StorageGateway(Base):
    """
    StorageGateway Model - Represents a storage gateways linked to a user.
    """
    __tablename__ = "storage_gateway"

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "type",
            name="uq_user_gateway_type"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    type = Column(
        Enum(
            StorageGatewayType,
            name="gateway_type",
            native_enum=False
        ),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: many StorageGateways belong to one User
    owner = relationship("User", back_populates="storage_gateways")

    telegram_gateway = relationship(
        "TelegramGateway",
        back_populates="storage_gateway",
        uselist=False,
        cascade="all, delete-orphan"
    )

    @validates("telegram_gateway")
    def validate_telegram_gateway(self, key, value):
        """
        Validate that TelegramGateway is only attached to TELEGRAM type StorageGateway.
        """
        if self.type != StorageGatewayType.TELEGRAM:
            raise ValueError(
                "TelegramGateway can only be attached to TELEGRAM storage gateway type"
            )
        return value


class TelegramGateway(Base):
    """
    User Model - Represents a user account.
    """
    __tablename__ = "telegram_gateway"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    storage_gateway_id = Column(
        Integer,
        ForeignKey("storage_gateway.id"),
        nullable=False,
        unique=True,
        index=True
    )

    storage_gateway = relationship(
        "StorageGateway",
        back_populates="telegram_gateway"
    )
