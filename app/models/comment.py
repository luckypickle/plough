from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String,func,DateTime

from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Comment(Base):
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    master_id = Column(Integer, ForeignKey("master.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    content = Column(String)
    rate = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    type = Column(Integer,default=0,comment="0 订单评论，1互动评论")
