from sqlalchemy import Column, DateTime, Integer, String, func, Text,ForeignKey
from app.db.base_class import Base

class Character(Base):
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    chars = Column(String, index=True, comment="字符")
    chars_wuxing = Column(String, index=True, comment="字符五行 0 - 无, 1 - 木, 2 - 火, 3 - 土, 4 - 金, 5 - 水")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")