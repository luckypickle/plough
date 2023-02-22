from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class HistoryEvent(Base):
    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer)
    event_type = Column(String)
    year = Column(Integer)
    year_gz = Column(String, comment="年干支")
    content = Column(String, comment="内容")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")