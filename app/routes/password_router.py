from fastapi import APIRouter, Body, Depends
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
    recover_data: RecoverPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        recover = srv.init_recover_password(db, recover_data.email)
        Logger().info(f"PIN sent to {recover_data.email}")
        return recover
    except APIException as e:
        Logger().err(str(e))
        raise APIExceptionToHTTP().convert(e)
