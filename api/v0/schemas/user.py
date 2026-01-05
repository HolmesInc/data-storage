from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a new user account"""
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user information in responses"""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CurrentUser(BaseModel):
    """Schema for current authenticated user"""
    id: int
    email: str
    username: str

    class Config:
        from_attributes = True

