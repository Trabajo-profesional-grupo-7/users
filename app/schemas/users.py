from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    preferences: Optional[List[str]] = []


class UserLogin(BaseModel):
    email: EmailStr = Field("example@email.com")
    password: str = Field("password", min_length=8)


class UserUpdate(UserBase):
    refresh_token: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field("password", min_length=8)


class User(UserBase):
    id: int

    class Config:
        from_attributes = True
