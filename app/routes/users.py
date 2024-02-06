from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import app.services.users_services as srv
from app.db.database import get_db
from app.schemas.token import *
from app.schemas.users import *
from app.utils.api_exception import APIException, APIExceptionToHTTP
from app.utils.logger import Logger

router = APIRouter()

security = HTTPBearer()


@router.post(
    "/users/signup",
    tags=["Auth"],
    status_code=201,
    response_model=User,
    description="Create a new user in the database",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = srv.new_user(db, user)
        Logger().info(f"User {new_user.username} created")
        return new_user
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.post(
    "/users/login",
    tags=["Auth"],
    status_code=200,
    response_model=Token,
    description="Generate a token for valid credentials",
)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    try:
        tokens = srv.new_login(db, user)
        Logger().info(f"User {user.email} logged in")
        return tokens
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.get(
    "/users/verify_id_token",
    tags=["Auth"],
    status_code=200,
    description="Authenticate user by the jwt token",
)
def verify_id_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    try:
        authenticated_id = srv.auth_user(credentials)
        Logger().info(f"User id {authenticated_id} authenticated")
        return authenticated_id
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.post(
    "/users/refresh_token",
    tags=["Auth"],
    status_code=200,
    response_model=Token,
    description="Refresh user token",
)
def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    try:
        tokens = srv.refresh_user_tokens(db, credentials)
        Logger().info(f"Refresh credentials")
        return tokens
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.patch(
    "/users",
    tags=["Users"],
    status_code=200,
    response_model=User,
    description="Update user profile",
)
def update_user_profile(
    updated_user: UserBase,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    try:
        user = srv.update_user(db, credentials, updated_user)
        Logger().info(f"User {user.id} updated")
        return user
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.delete(
    "/users",
    tags=["Users"],
    status_code=200,
    response_model=User,
    description="Delete user profile",
)
def delete_user_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    try:
        db_user = srv.delete_user(db, credentials)
        Logger().info(f"User {db_user.id} deleted")
        return db_user
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.get(
    "/users",
    tags=["Users"],
    status_code=200,
    response_model=User,
    description="Get user info",
)
def get_user_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    try:
        authenticated_id = srv.get_user(db, credentials)
        Logger().info(f"User id {authenticated_id} authenticated")
        return authenticated_id
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)
