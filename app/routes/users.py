from fastapi import APIRouter, Depends, HTTPException

import app.services.users_services as srv
from app.db import schemas
from app.db.database import SessionLocal, get_db
from app.util.api_exception import APIException, APIExceptionToHTTP
from app.util.logger import Logger

router = APIRouter()


@router.post(
    "/users/",
    tags=["Users"],
    status_code=201,
    response_model=schemas.User,
    description="Create a new user in the database",
)
def create_user(user: schemas.UserCreate, db: SessionLocal = Depends(get_db)):
    try:
        user = srv.new_user(db, user)
        Logger().info(f"User {user.username} created")
        return user
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)
