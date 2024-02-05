from sqlalchemy import JSON, Column, Date, Integer, String

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
