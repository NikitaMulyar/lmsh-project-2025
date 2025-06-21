import uuid

from sqlalchemy import Column, String, Integer, Text, orm
from server.backend.database import SqlAlchemyBase


class Event(SqlAlchemyBase):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)  # Название олимпиады/события. Нет строгих требований (нельзя писать в
    # конце год, он дописывается где нужно сам). Можно писать что угодно
    subject = Column(String, nullable=True)  # Предмет
    rsosh_level = Column(Integer, nullable=True)  # Для олимпиад РСОШ используется для сортировки, для остальных -
    # для разграничения типов и сортировки
    year = Column(Integer, nullable=False)  # Год олимпиады
    extra = Column(Text, nullable=True)  # Любая доп. информация

    olymp_code = Column(String, nullable=True)  # Код олимпиады. Например: ЕГЭ, ОГЭ, ВсОШ, МОШ, PROD
    olymp = Column(String, nullable=True)  # Краткое название олимпиады (без предмета) (используется для группировки).
    # Например: ЕГЭ, ЗЭ ВсОШ, МЭ ВсОШ, МОШ, PROD
    stage_code = Column(String, nullable=True) # Код этапа. Например: ОЭ (отборочный), ЗЭ (заключительный)
    stage = Column(String, nullable=True) # Полное название этапа. Например: Заключительный, Отборочный
    english_olymp_code = Column(String, nullable=True) # Код олимпиады на английском. Например: prod, vos, mosh
    english_stage_code = Column(String, nullable=True) # Код этапа на английском. Например: invite, school, municip,
    # region, finals, qualify

    records = orm.relationship("Record", back_populates="event",
                               cascade="all, delete", uselist=True)
