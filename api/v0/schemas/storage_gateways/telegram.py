from pydantic import BaseModel, Field


class CreateTelegramGateway(BaseModel):
    """Schema to register a Telegram storage gateway"""
    chat_id: str = Field(..., description="ID received from TelegramCloud chatbot")


class CreateTelegramGatewayResponse(BaseModel):
    """Schema for response after registering a Telegram storage gateway"""
    status: bool = Field(True, description="Operation status")
    message: str = Field(..., description="A short description of operation results")


class GetTelegramGateway(BaseModel):
    """Schema to get a Telegram storage gateway data for a user"""
    chat_id: str = Field(..., description="ID received from TelegramCloud chatbot")


class UpdateTelegramGateway(CreateTelegramGateway):
    """Schema to update a Telegram storage gateway"""
    pass

class UpdateTelegramGatewayResponse(CreateTelegramGatewayResponse):
    """Schema for response after updating a Telegram storage gateway"""
    pass
