from datetime import datetime

from pydantic import BaseModel, EmailStr


class RecoverPasswordRequest(BaseModel):
    email: EmailStr


class PasswordRecover(BaseModel):
    user_id: int
    emited_datetime: datetime
    leftover_attempts: int

    class Config:
        from_attributes = True


class PasswordRecoverCreate(PasswordRecover):
    pin: str
