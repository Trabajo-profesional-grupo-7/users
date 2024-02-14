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
    db_pwd_recover = models.PasswordRecover(
        user_id=recover.user_id,
        pin=recover.pin,
        emited_datetime=recover.emited_datetime,
    )

    db.add(db_pwd_recover)
    db.commit()
    db.refresh(db_pwd_recover)
    return db_pwd_recover


def update_recover_attemps(db: Session, id: int):
    db_recover = (
        db.query(models.PasswordRecover)
        .filter(models.PasswordRecover.user_id == id)
        .first()
    )

    setattr(db_recover, "leftover_attempts", db_recover.leftover_attempts - 1)

    db.commit()
    db.refresh(db_recover)
    return db_recover


def delete_recover(db: Session, id: int) -> models.PasswordRecover | None:
    db_recover = get_recover(db, id)

    if db_recover:
        db.delete(db_recover)
        db.commit()
        return db_recover

    return None
