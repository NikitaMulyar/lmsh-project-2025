import uuid

from sqlalchemy import Column, String, ForeignKey, orm
from server.backend.database import SqlAlchemyBase


class Record(SqlAlchemyBase):
    __tablename__ = "records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    event_id = Column(String, ForeignKey("events.id"))
    status = Column(String, nullable=True)

    user = orm.relationship("User", back_populates="records")
    event = orm.relationship("Event", back_populates="records")
