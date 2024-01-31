from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field("username", min_length=4)
    email: EmailStr = Field("example@email.com")
    birth_date: date


class UserLogin(BaseModel):
    email: EmailStr = Field("example@email.com")
    password: str = Field("password", min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    birth_date: Optional[date]
    refresh_token: Optional[str]


class UserCreate(UserBase):
    password: str = Field("password", min_length=8)


class User(UserBase):
    id: int

    class Config:
        from_attributes = True
