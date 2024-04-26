from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import app.services.users_services as srv
from app.db.database import get_db
from app.schemas.chat import Chat
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
        authenticated_user = srv.get_user(db, credentials)
        Logger().info(f"User id {authenticated_user.id} authenticated")
        return authenticated_user
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.post(
    "/users/chat",
    tags=["Users"],
    status_code=200,
    response_model=User,
    description="Create a new chat for a user",
)
def new_chat(chat: Chat, db: Session = Depends(get_db)):
    try:
        user = srv.new_chat_ids(db, chat)
        Logger().info(f"New chat for user id {user.id}")
        return user
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.get(
    "/users/{id}/chat",
    tags=["Users"],
    status_code=200,
    response_model=Chat,
    description="Get user chat",
)
def user_chat(
    id: int,
    db: Session = Depends(get_db),
):
    try:
        chat = srv.get_user_chat(db, id)
        Logger().info(f"Get user {chat.user_id} chat")
        return chat
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.get(
    "/users/{id}/preferences",
    tags=["Users"],
    status_code=200,
    response_model=list[str],
    description="Get user preferences",
)
def user_preferences(
    id: int,
    db: Session = Depends(get_db),
):
    try:
        preferences = srv.get_user_preferences(db, id)
        Logger().info(f"Get user {id} preferences")
        return preferences
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)
