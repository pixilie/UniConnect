import time

from psycopg2 import OperationalError as Psycopg2OpError
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

MAX_RETRIES = 5
RETRY_DELAY = 2

for i in range(MAX_RETRIES):
    try:
        time.sleep(RETRY_DELAY)
        with engine.connect() as connection:
            print("Connection to DB established")
            break
    except (OperationalError, Psycopg2OpError):
        print(f"DB not ready... Retry in {RETRY_DELAY} seconds ({i + 1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)
else:
    print("Impossible to connect to DB")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
