import os
import secrets
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth import authentication as auth
from app.auth import password as pwd
from app.db import pwd_recover_crud, user_crud
from app.schemas.password import *
from app.utils.api_exception import APIException
from app.utils.constants import *

EMAIL = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(pin: int, email: str):
    body = f"""
          <!DOCTYPE html>
          <html lang="en">
          <head>
              <meta charset="UTF-8">
              <meta http-equiv="X-UA-Compatible" content="IE=edge">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Password Recover</title>
              <style>
                  body {{
                      font-family: Arial, sans-serif;
                      background-color: #f4f4f4;
                  }}
                  .container {{
                      max-width: 600px;
                      margin: 0 auto;
                      padding: 20px;
                      background-color: #DAF8B8;
                      border-radius: 10px;
                      box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                  }}
                  h1 {{
                      color: #000000; 
                      text-align: center;
                  }}
                  p {{
                      color: #333;
                  }}
              </style>
          </head>
          <body>
              <div class="container">
                  <h1>Password recover</h1>
                  <h3>Tu código para reestablecer tu contraseña es:</h3>
                  <h3 style="font-size: 24px; font-weight: bold; text-align: center;">{pin}</h3>
                  <h4>Por favor, no compartas este código.</h4>
              </div>
          </body>
          </html>
         """

    em = EmailMessage()
    em["From"] = EMAIL
    em["To"] = email
    em["subject"] = "Password Recover"
    em.set_content(body)
    em.set_content(body, subtype="html")

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(user=EMAIL, password=PASSWORD)
        smtp.sendmail(EMAIL, email, em.as_string())

    return pin


def init_recover_password(db: Session, email: str) -> PasswordRecover:
    db_user = user_crud.get_user_by_email(db, email)

    if not db_user:
        raise APIException(code=USER_DOES_NOT_EXISTS_ERROR, msg="Email not found")

    if pwd_recover_crud.get_recover(db, db_user.id):
        raise APIException(
            code=RECOVER_ALREADY_INITIATED_ERROR, msg=f"Pin alredy sent to {email}"
        )

    pin = secrets.token_hex(3)
    send_email(pin, email)

    recover = PasswordRecoverCreate.model_construct(
        user_id=db_user.id, emited_datetime=datetime.now(), pin=pin
    )

    return pwd_recover_crud.new_pwd_recover(db, recover)


def recover_password(
    db: Session,
    credentials: HTTPAuthorizationCredentials,
    recover_data: UpdateRecoverPassword,
):
    user_id = auth.get_current_user(credentials.credentials)

    if credentials.scheme != "Bearer" or not user_id:
        raise APIException(code=INVALID_HEADER_ERROR, msg="Not authenticated")

    db_recover = pwd_recover_crud.get_recover(db, user_id)
    if not db_recover:
        raise APIException(
            code=RECOVERY_NOT_INITIATED_ERROR,
            msg="The user did not initiate the password recovery process",
        )

    if db_recover.pin == recover_data.code:
        hashed_password = pwd.get_password_hash(recover_data.new_password)
        db_user = user_crud.update_user_pwd(db, user_id, hashed_password)
        pwd_recover_crud.delete_recover(db, user_id)
        return db_user.id, "Password updated"

    db_recover = pwd_recover_crud.update_recover_attemps(db, user_id)
    if db_recover.leftover_attempts == 0:
        pwd_recover_crud.delete_recover(db, user_id)

    return user_id, "Invalid code"
