from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Master(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String,unique=True,index=True)
    hashed_password = Column(String, nullable=False)
    avatar = Column(String, comment="头像")
    desc = Column(String, comment="老师介绍")
    rate = Column(Integer, nullable=False, comment="分成比例")
    price = Column(Integer, comment="排盘价格")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    order_number = Column(Integer, default=0, comment="订单数量")
    status = Column(Integer, index=True, comment="状态: 0 - 未激活, 1 - 激活, 2 - 失效, 3 - 待激活")
    orders = relationship("Order", back_populates="master")
    order_amount = Column(Integer, default=0, comment="订单金额")
