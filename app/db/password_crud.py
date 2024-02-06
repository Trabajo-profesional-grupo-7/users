from sqlalchemy.orm import Session

import app.schemas.password as schemas

from . import models


def get_recover(db: Session, user_id: int):
    return (
        db.query(models.PasswordRecover)
        .filter(models.PasswordRecover.user_id == user_id)
        .first()
    )


def new_pwd_recover(
    db: Session, recover: schemas.PasswordRecoverCreate
) -> models.PasswordRecover:

    print(recover)

    db_pwd_recover = models.PasswordRecover(
        user_id=recover.user_id,
        pin=recover.pin,
        emited_datetime=recover.emited_datetime,
    )

    db.add(db_pwd_recover)
    db.commit()
    db.refresh(db_pwd_recover)
    return db_pwd_recover
