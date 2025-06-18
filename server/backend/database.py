import os
from dotenv import load_dotenv

from sqlalchemy import orm, create_engine
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec


if not os.path.exists('./db/'):
    os.mkdir('./db/')

load_dotenv()

SqlAlchemyBase = dec.declarative_base()

DB_FILE = os.getenv("DB_FILE", "sqlite.db")
DATABASE_URL = f"sqlite:///{DB_FILE}?check_same_thread=False"

engine = create_engine(DATABASE_URL, echo=False, pool_timeout=60, pool_size=100, max_overflow=200)
SessionLocal = orm.sessionmaker(bind=engine, expire_on_commit=False)

from server.models import __all_models

SqlAlchemyBase.metadata.create_all(engine)


def get_session() -> Session:
    return SessionLocal()
