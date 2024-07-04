from sqlalchemy.orm import Session

import app.schemas.users as schemas
from app.schemas.chat import Chat

from . import models


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        city=user.city,
        birth_date=user.birth_date,
        preferences=user.preferences,
        hashed_password=user.password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> models.User:
    db_user = get_user(db, user_id)

    for var, value in vars(user).items():
        if value or var == "preferences":
            setattr(db_user, var, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_fcm_token(db: Session, user_id: int, fcm_token: str) -> models.User:
    db_user = get_user(db, user_id)

    setattr(db_user, "fcm_token", fcm_token)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_pwd(db: Session, user_id: int, new_password: str) -> models.User:
    db_user = get_user(db, user_id)

    setattr(db_user, "hashed_password", new_password)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> models.User | None:
    db_user = get_user(db, user_id)

    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user

    return None


def update_user_chat(db: Session, chat: Chat) -> models.User | None:
    db_user = get_user(db, chat.user_id)

    setattr(db_user, "thread_id", chat.thread_id)
    setattr(db_user, "assistant_id", chat.assistant_id)

    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_chat(db: Session, user_id: int) -> Chat:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    thread_id = db_user.thread_id
    assistant_id = db_user.assistant_id
    return Chat.model_construct(
        user_id=user_id, thread_id=thread_id, assistant_id=assistant_id
    )


def get_user_preferences(db: Session, user_id: int) -> list[str]:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    return db_user.preferences
