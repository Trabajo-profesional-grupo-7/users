import os
from datetime import datetime, timedelta

import jwt

from app.db import crud, models
from app.utils.api_exception import APIException
from app.utils.constants import EXPIRED_TOKEN, INVALID_CREDENTIALS

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authorize_token(token: str) -> models.User:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        exp = payload.get("exp")
        if user_id is None or exp is None:
            raise APIException(
                code=INVALID_CREDENTIALS, msg="Could not validate credentials"
            )

        return user_id
    except Exception as e:
        raise APIException(code=EXPIRED_TOKEN, msg=str(e))


def get_current_user(token: str) -> int | None:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        if not payload:
            return None

        return payload.get("sub")
    except Exception as e:
        raise APIException(code=EXPIRED_TOKEN, msg=str(e))
