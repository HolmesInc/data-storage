"""
Pydantic Schemas Module

Pydantic schemas define the structure of data sent to and from the API.
They provide data validation and automatic documentation in Swagger.
"""
from pydantic import (
    BaseModel,
    Field,
)
from datetime import datetime
from typing import Optional


class FileBase(BaseModel):
    """Base schema with common file fields"""
    name: str = Field(..., description="Name of the file")
    folder_id: int = Field(..., description="ID of the folder containing this file")


class FileCreate(FileBase):
    """Schema for creating a file (used in POST requests)"""
    pass


class FileUpdate(BaseModel):
    """Schema for updating a file (renaming)"""
    name: str = Field(..., description="New name for the file")


class FileResponse(FileBase):
    """
    Schema for file responses from the API.
    This is what the API returns when you request file data.
    """
    id: int
    file_path: str = Field(..., description="Path to the file on disk")
    file_size: int = Field(..., description="Size of the file in bytes")
    file_type: str = Field(default="pdf", description="Type of file")
    created_at: datetime
    updated_at: datetime

    # Config that allows converting SQLAlchemy models to Pydantic models
    class Config:
        from_attributes = True


class FileShareCreate(BaseModel):
    """Schema for creating a file share"""
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date for the share")


class FileShareResponse(BaseModel):
    """Schema for file share responses"""
    id: int
    file_id: int
    token: str = Field(..., description="Unique token for the share link")
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True
