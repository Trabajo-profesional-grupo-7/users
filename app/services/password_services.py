import os
import secrets
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.db import password_crud, user_crud
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

    if password_crud.get_recover(db, db_user.id):
        raise APIException(
            code=RECOVER_ALREADY_INITIATED_ERROR, msg=f"Pin alredy sent to {email}"
        )

    pin = secrets.token_hex(3)
    send_email(pin, email)

    recover = PasswordRecoverCreate.model_construct(
        user_id=db_user.id, emited_datetime=datetime.now(), pin=pin
    )

    return password_crud.new_pwd_recover(db, recover)
