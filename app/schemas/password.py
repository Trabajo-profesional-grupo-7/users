from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class InitRecoverPassword(BaseModel):
    email: EmailStr


class UpdateRecoverPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field("password", min_length=8)


class PasswordRecover(BaseModel):
    user_id: int
    emited_datetime: datetime
    leftover_attempts: int

    class Config:
        from_attributes = True


class PasswordRecoverCreate(PasswordRecover):
    pin: str
