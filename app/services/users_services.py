from sqlalchemy.exc import SQLAlchemyError

from app.db import crud, schemas
from app.db.database import SessionLocal
from app.util.api_exception import APIException
from app.util.constants import *
from app.util.logger import Logger


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


def new_user(db: SessionLocal, user: schemas.UserCreate) -> schemas.UserCreate:
    def create_user_logic():
        db_user_email = crud.get_user_by_email(db, email=user.email)
        if db_user_email:
            raise APIException(
                code=USER_EXISTS_ERROR, msg=f"Email {user.email} already used"
            )
        return crud.create_user(db=db, user=user)

    return exception_handler(create_user_logic)
