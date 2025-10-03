from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    username: str
    role: Optional[str] = "user"

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return to client
class User(UserBase):
    id: int
    created_at: datetime
    reset_password_token: Optional[str] = None
    reset_password_token_expiry: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for JWT Token
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

# Schema for data stored in JWT
class TokenData(BaseModel):
    username: Optional[str] = None
