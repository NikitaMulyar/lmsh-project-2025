import uuid

from sqlalchemy import Column, String, Integer, Text, orm
from server.backend.database import SqlAlchemyBase


class Event(SqlAlchemyBase):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    extra = Column(Text, nullable=True)

    records = orm.relationship("Record", back_populates="event",
                               cascade="all, delete", uselist=True)
