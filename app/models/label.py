from sqlalchemy import Column, DateTime, Integer, String, func
from app.db.base_class import Base


class Label(Base):
    id = Column(Integer, primary_key=True, index=True)
    label_name = Column(String, index=True, comment="标签名称")
    user_id = Column(Integer, index=True)
    label_type = Column(Integer,default=0, index=True, comment="状态: 0 - 公有的, 1 - 用户私有的")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")