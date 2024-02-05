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
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
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
def login_user(user: UserLogin, db: Session = Depends(get_db)) -> User:
    try:
        jwt = srv.new_login(db, user)
        Logger().info(f"User {user.email} logged in")
        return jwt
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
