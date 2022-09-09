from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Favorite(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("user.id"))
    order_id = Column(Integer,ForeignKey("order.id"))
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    status = Column(Integer,default=0, index=True, comment="状态: 0 - 显示, 1 - 隐藏")

