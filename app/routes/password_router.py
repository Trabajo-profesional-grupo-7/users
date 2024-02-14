from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import app.services.password_services as srv
from app.db.database import get_db
from app.schemas.password import *
from app.schemas.token import *
from app.schemas.users import *
from app.utils.api_exception import APIException, APIExceptionToHTTP
from app.utils.logger import Logger

router = APIRouter()

security = HTTPBearer()


@router.post(
    "/users/password/recover",
    tags=["Password"],
    status_code=200,
    response_model=PasswordRecover,
    description="Send pin by email to recover the password",
)
def init_recover_password(
    recover_data: InitRecoverPassword,
    db: Session = Depends(get_db),
):
    try:
        recover = srv.init_recover_password(db, recover_data.email)
        Logger().info(f"PIN sent to {recover_data.email}")
        return recover
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)


@router.put(
    "/users/password/recover",
    tags=["Password"],
    status_code=200,
    description="Receive the code and the new password and update it if the code match",
)
def recover_password(
    recover_data: UpdateRecoverPassword,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    try:
        user_id, detail = srv.recover_password(db, credentials, recover_data)
        Logger().info(f"User {user_id}: {detail}")
        return {"user_id": user_id, "detail": detail}
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)
