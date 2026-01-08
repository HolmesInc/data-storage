from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .folder import FolderResponse



class DataRoomBase(BaseModel):
    """Base schema with common data room fields"""
    name: str = Field(..., description="Name of the data room")
    description: Optional[str] = Field(None, description="Description of the data room")


class DataRoomCreate(DataRoomBase):
    """Schema for creating a data room"""
    pass


class DataRoomUpdate(BaseModel):
    """Schema for updating a data room"""
    name: Optional[str] = Field(None, description="New name for the data room")
    description: Optional[str] = Field(None, description="New description for the data room")


class DataRoomResponse(DataRoomBase):
    """
    Schema for data room responses - includes all nested folders and files.
    This is the complete hierarchical structure.
    """
    id: int
    created_at: datetime
    updated_at: datetime
    folders: List[FolderResponse] = []

    class Config:
        from_attributes = True


class DataRoomListResponse(DataRoomBase):
    """
    Lightweight schema for listing data rooms.
    Used when returning multiple data rooms to reduce payload size.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
