from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    city: Optional[str] = None
    preferences: Optional[List[str]] = []


class UserLogin(BaseModel):
    email: EmailStr = Field("user@example.com")
    password: str = Field("password", min_length=8)


class UserUpdate(UserBase):
    refresh_token: Optional[str] = None
    avatar_link: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field("password", min_length=8)
    fcm_token: str


class User(UserBase):
    id: int
    avatar_link: Optional[str] = None

    class Config:
        from_attributes = True
