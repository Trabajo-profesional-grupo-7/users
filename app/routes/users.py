from fastapi import APIRouter
from fastapi import Depends, HTTPException

from app.db import crud, schemas
from app.db.database import SessionLocal, get_db
from app.services.logger import Logger

router = APIRouter()


@router.post("/users/", response_model=schemas.User, status_code=201, tags=["Users"])
def create_user(user: schemas.UserCreate, db: SessionLocal = Depends(get_db)):
    db_user_email = crud.get_user_by_email(db, email=user.email)
    db_user_username = crud.get_user_by_username(db, username=user.username)
    if db_user_email or db_user_username:
        Logger().info("User alredy exists")
        raise HTTPException(
            status_code=409, detail={"status": "error", "message": "Email already registered"})

    return crud.create_user(db=db, user=user)
