from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.ANALYST
    is_active: bool = True
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.ANALYST


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
