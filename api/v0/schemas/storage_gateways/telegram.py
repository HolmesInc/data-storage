from pydantic import BaseModel, Field


class CreateTelegramGateway(BaseModel):
    """Schema to register a Telegram storage gateway"""
    chat_id: str = Field(..., description="ID received from TelegramCloud chatbot")


class CreateTelegramGatewayResponse(BaseModel):
    """Schema for response after registering a Telegram storage gateway"""
    status: bool = Field(True, description="Operation status")
    message: str = Field(..., description="A short description of operation results")
