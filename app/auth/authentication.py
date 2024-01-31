import os
from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.db import crud, models
from app.utils.api_exception import APIException
from app.utils.constants import EXPIRED_TOKEN

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str) -> models.User:
    credentials_exception = APIException(
        code=EXPIRED_TOKEN, msg="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        exp = payload.get("exp")
        if user_id is None or exp is None:
            raise credentials_exception

        if datetime.utcfromtimestamp(exp) < datetime.now():
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user(user_id=user_id)
    if user is None:
        raise credentials_exception
    return user
