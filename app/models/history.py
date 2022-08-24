from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class History(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sex = Column(Integer, index=True)
    birthday = Column(String)
    location = Column(String, index=True)
    divination = Column(String)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="history", foreign_keys=[owner_id])
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    status = Column(Integer, index=True, comment="状态: 0 - 显示, 1 - 隐藏")
