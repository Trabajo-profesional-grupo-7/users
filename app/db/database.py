import os
import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_user = urllib.parse.quote_plus(os.getenv("POSTGRES_USER"))
db_password = urllib.parse.quote_plus(os.getenv("POSTGRES_PASSWORD"))
db_name = urllib.parse.quote_plus(os.getenv("POSTGRES_DB"))
db_service = urllib.parse.quote_plus(os.getenv("POSTGRES_SERVICE"))

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_service}/{db_name}"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
