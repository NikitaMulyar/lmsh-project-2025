import uuid

from sqlalchemy import Column, String, Integer, orm
from server.backend.database import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fio = Column(String, nullable=False)
    grade_number = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)
    graduate_year = Column(Integer, nullable=False)
    profile = Column(String, nullable=True)

    records = orm.relationship("Record", back_populates="user",
                               cascade="all, delete", uselist=True)
