from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import crud, models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str) -> models.User:
    user = crud.get_user_by_email(db, email)

    if not user or not verify_password(password, user.hashed_password):
        return None

    return user
