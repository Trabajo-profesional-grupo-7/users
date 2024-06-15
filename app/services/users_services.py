import os
import secrets

import requests
from fastapi import UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth import authentication as auth
from app.auth import password as pwd
from app.db import models, user_crud
from app.ext import firebase as fb
from app.schemas.chat import Chat
from app.schemas.token import *
from app.schemas.users import *
from app.utils.api_exception import APIException
from app.utils.constants import *
from app.utils.logger import Logger

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
ATTRACTIONS_SERVICE = os.getenv("ATTRACTIONS_SERVICE")

# COMMON


def update_recommendations(user_id: int, default_city: str, preferences: List[str]):
    response = requests.put(
        f"{ATTRACTIONS_SERVICE}/update_recommendations",
        json={
            "user_id": user_id,
            "default_city": default_city,
            "preferences": preferences,
        },
    )

    if response.status_code == 200:
        Logger().info(f"User {user_id} update recommendations")
    else:
        Logger().err(f"Error updating user {user_id} recommendations")


def exception_handler(action):
    try:
        return action()
    except SQLAlchemyError as e:
        raise APIException(
            code=DATABASE_ERROR, msg=f"Database transaction error: {str(e)}"
        )
    except Exception as e:
        if isinstance(e, APIException):
            raise e
        raise APIException(code=UNKNOWN_ERROR, msg="Unknown error")


def create_session_tokens(db: Session, user: models.User):
    token = auth.create_access_token(
        data={"sub": user.id}, expires_delta=int(ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    random_secret = secrets.token_hex(8)
    refresh_token = auth.create_access_token(
        data={"sub": user.id, "secret": random_secret}
    )

    user_update = UserUpdate.model_construct(
        username=user.username,
        email=user.email,
        birth_date=user.birth_date,
        preferences=user.preferences,
        refresh_token=refresh_token,
    )

    user_crud.update_user(db, user.id, user_update)

    return Token.model_construct(
        token=token, refresh_token=refresh_token, token_type="jwt"
    )


# SERVICES


def new_user(db: Session, user: UserCreate) -> UserCreate:
    def create_user_logic():
        db_user_email = user_crud.get_user_by_email(db, email=user.email)
        if db_user_email:
            raise APIException(
                code=USER_EXISTS_ERROR, msg=f"Email {user.email} already used"
            )
        user.password = pwd.get_password_hash(user.password)
        db_user = user_crud.create_user(db=db, user=user)
        update_recommendations(db_user.id, user.city, user.preferences)
        return db_user

    return exception_handler(create_user_logic)


def new_login(db: Session, user: UserLogin) -> Token:
    def log_user_logic():
        db_user = pwd.authenticate_user(db, user.email, user.password)

        if not db_user:
            raise APIException(code=LOGIN_ERROR, msg=f"Invalid credentials")

        return create_session_tokens(db, db_user)

    return exception_handler(log_user_logic)


def auth_user(credentials: HTTPAuthorizationCredentials) -> int:
    if credentials.scheme != "Bearer":
        raise APIException(code=INVALID_HEADER_ERROR, msg="Not authenticated")

    return auth.authorize_token(credentials.credentials)


def refresh_user_tokens(
    db: Session, credentials: HTTPAuthorizationCredentials
) -> Token:
    def refresh_token_logic():
        if credentials.scheme != "Bearer":
            raise APIException(code=INVALID_HEADER_ERROR, msg="Not authenticated")

        user_id = auth.get_current_user(credentials.credentials)

        db_user = user_crud.get_user(db, user_id)
        if db_user.refresh_token != credentials.credentials:
            raise APIException(
                code=INVALID_CREDENTIALS_ERROR, msg="Invalid refresh token"
            )

        return create_session_tokens(db, db_user)

    return exception_handler(refresh_token_logic)


def update_user(
    db: Session,
    credentials: HTTPAuthorizationCredentials,
    updated_user: UserBase,
) -> User:
    def update_user_logic():
        if credentials.scheme != "Bearer":
            raise APIException(code=INVALID_HEADER_ERROR, msg="Not authenticated")

        user_id = auth.get_current_user(credentials.credentials)

        db_user = user_crud.update_user(db, user_id, updated_user)
        if not db_user:
            raise APIException(
                code=USER_DOES_NOT_EXISTS_ERROR, msg="User does not exist"
            )

        if updated_user.preferences or updated_user.city:
            update_recommendations(user_id, db_user.city, db_user.preferences)

        return db_user

    return exception_handler(update_user_logic)


def update_password(db: Session, user_id: int, new_password_hashed: str) -> User:
    return user_crud.update_user_pwd(db, user_id, new_password_hashed)


def delete_user(db: Session, credentials: HTTPAuthorizationCredentials) -> User:
    def delete_user_logic():
        if credentials.scheme != "Bearer":
            raise APIException(code=INVALID_HEADER_ERROR, msg="Not authenticated")

        user_id = auth.get_current_user(credentials.credentials)

        db_user = user_crud.delete_user(db, user_id)
        if not db_user:
            raise APIException(
                code=USER_DOES_NOT_EXISTS_ERROR, msg="User does not exist"
            )

        return db_user

    return exception_handler(delete_user_logic)


def get_user(db: Session, id: int) -> User:
    def get_user_logic():
        db_user = user_crud.get_user(db, id)

        if not db_user:
            raise APIException(
                code=USER_DOES_NOT_EXISTS_ERROR, msg="User does not exist"
            )

        return db_user

    return exception_handler(get_user_logic)


def new_chat_ids(db: Session, chat: Chat) -> User:
    def new_chat_ids_logic():
        db_user = user_crud.update_user_chat(db, chat)

        if not db_user:
            raise APIException(
                code=USER_DOES_NOT_EXISTS_ERROR, msg="User does not exist"
            )

        return db_user

    return exception_handler(new_chat_ids_logic)


def get_user_chat(db: Session, user_id: int) -> Chat:
    def get_chat_ids_logic():
        db_chat = user_crud.get_user_chat(db, user_id)

        if not db_chat:
            raise APIException(
                code=USER_DOES_NOT_EXISTS_ERROR, msg="User does not exist"
            )

        return db_chat

    return exception_handler(get_chat_ids_logic)


def get_user_preferences(db: Session, user_id: int) -> list[str]:
    def get_user_preferences_logic():
        db_preferences = user_crud.get_user_preferences(db, user_id)

        if not db_preferences:
            return []

        return db_preferences

    return exception_handler(get_user_preferences_logic)


def update_avatar(
    db: Session, credentials: HTTPAuthorizationCredentials, avatar: UploadFile
) -> User:
    def get_user_preferences_logic():
        if credentials.scheme != "Bearer":
            raise APIException(code=INVALID_HEADER_ERROR, msg="Not authenticated")

        user_id = auth.get_current_user(credentials.credentials)

        avatar_link = fb.upload_image(
            "avatars",
            avatar.content_type,
            avatar.file,
            str(user_id) + " " + avatar.filename,
        )
        db_user = user_crud.update_user(
            db, user_id, UserUpdate(avatar_link=avatar_link)
        )

        return db_user

    return exception_handler(get_user_preferences_logic)
