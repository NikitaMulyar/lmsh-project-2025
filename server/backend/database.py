import os
from contextlib import contextmanager

from sqlalchemy import orm, create_engine
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec


if not os.path.exists('db/'):
    os.mkdir('db/')


SqlAlchemyBase = dec.declarative_base()
SessionLocal = None


def create_db():
    global SessionLocal

    DB_FILE = 'db/' + os.getenv("DB_FILE", "sqlite.db")
    DATABASE_URL = f"sqlite:///{DB_FILE}?check_same_thread=False"

    engine = create_engine(DATABASE_URL, echo=False, pool_timeout=60, pool_size=100, max_overflow=200)
    SessionLocal = orm.sessionmaker(bind=engine, expire_on_commit=False)

    from server.models import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
