from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class HistoryCombine(Base):
    id = Column(Integer, primary_key=True, index=True)
    name1 = Column(String, index=True)
    sex1 = Column(Integer, index=True)
    birthday1 = Column(String)
    location1 = Column(String, index=True)
    divination1 = Column(String)
    isNorth1 = Column(Boolean, default=True, comment="是否北半球")
    name2 = Column(String, index=True)
    sex2 = Column(Integer, index=True)
    birthday2 = Column(String)
    location2 = Column(String, index=True)
    divination2 = Column(String)
    isNorth2 = Column(Boolean, default=True, comment="是否北半球")
    owner_id = Column(Integer, ForeignKey("user.id"))
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")

