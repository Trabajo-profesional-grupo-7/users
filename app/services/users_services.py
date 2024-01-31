import os
import secrets
import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth import authentication as auth
from app.auth import password as pwd
from app.db import crud
from app.schemas.token import *
from app.schemas.users import *
from app.utils.api_exception import APIException
from app.utils.constants import *

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


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


def new_user(db: Session, user: UserCreate) -> UserCreate:
    def create_user_logic():
        db_user_email = crud.get_user_by_email(db, email=user.email)
        if db_user_email:
            raise APIException(
                code=USER_EXISTS_ERROR, msg=f"Email {user.email} already used"
            )
        user.password = pwd.get_password_hash(user.password)
        return crud.create_user(db=db, user=user)

    return exception_handler(create_user_logic)


def new_login(db: Session, user: UserLogin) -> Token:
    def log_user_logic():
        db_user = pwd.authenticate_user(db, user.email, user.password)

        if not user:
            raise APIException(code=LOGIN_ERROR, msg=f"Invalid credentials")

        token = auth.create_access_token(
            {"sub": db_user.id}, int(ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        random_secret = secrets.token_hex(8)
        refresh_token = auth.create_access_token(
            {"sub": db_user.id, "secret": random_secret}
        )

        user_update = UserUpdate.model_construct(
            username=db_user.username,
            email=db_user.email,
            birth_date=db_user.birth_date,
            refresh_token=refresh_token,
        )

        crud.update_user(db, db_user.id, user_update)

        return Token.model_construct(
            token=token, refresh_token=refresh_token, token_type="jwt"
        )

    return exception_handler(log_user_logic)
