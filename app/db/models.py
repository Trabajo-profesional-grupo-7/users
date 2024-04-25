from sqlalchemy import JSON, Column, Date, DateTime, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String, unique=True)
    birth_date = Column(Date)
    preferences = Column(JSON, default=None)
    hashed_password = Column(String)
    refresh_token = Column(String, nullable=True, default=None)
    thread_id = Column(String, nullable=True, default=None)
    assistant_id = Column(String, nullable=True, default=None)


class PasswordRecover(Base):

    __tablename__ = "password_recover"

    user_id = Column(Integer, primary_key=True)
    pin = Column(String)
    emited_datetime = Column(DateTime)
    leftover_attempts = Column(Integer, default=3)
