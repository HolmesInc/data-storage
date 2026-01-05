"""
Pydantic Schemas Module

Pydantic schemas define the structure of data sent to and from the API.
They provide data validation and automatic documentation in Swagger.
"""
from pydantic import (
    BaseModel,
    Field,
)
from typing import (
    Optional,
    List,
)
from datetime import datetime

from .file import FileResponse


class FolderBase(BaseModel):
    """Base schema with common folder fields"""
    name: str = Field(..., description="Name of the folder")
    dataroom_id: int = Field(..., description="ID of the data room")


class FolderCreate(FolderBase):
    """Schema for creating a folder"""
    parent_id: Optional[int] = Field(None, description="ID of parent folder (for nesting)")


class FolderUpdate(BaseModel):
    """Schema for updating a folder (renaming)"""
    name: str = Field(..., description="New name for the folder")


class FolderResponse(FolderBase):
    """
    Schema for folder responses - includes nested files and subfolders.
    This shows the complete folder structure.
    """
    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    files: List[FileResponse] = []
    subfolders: List["FolderResponse"] = []

    class Config:
        from_attributes = True


# Update forward reference for recursive type
FolderResponse.model_rebuild()