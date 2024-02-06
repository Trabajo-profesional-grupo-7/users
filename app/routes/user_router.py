from typing import Annotated

from fastapi import APIRouter, Depends
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
