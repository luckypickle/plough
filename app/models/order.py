from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401

class Order(Base):
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    name = Column(String, index=True)
    sex = Column(Integer, index=True)
    birthday = Column(String)
    location = Column(String, index=True)
    amount = Column(Integer, comment="金额，单位'分'")
    pay_type = Column(String, index=True)
    channel = Column(Integer, comment="渠道")
    shareRate = Column(Integer, comment="订单分成")
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="orders", foreign_keys=[owner_id])
    master_id = Column(Integer, ForeignKey("master.id"))
    master = relationship("Master", back_populates="orders", foreign_keys=[master_id])
    divination = Column(String)
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    pay_time = Column(DateTime, server_default=func.now(), index=True, comment="支付时间")
    arrange_status = Column(Integer, comment="排盘状态：0 - 未排盘, 1 - 已排盘")
    status = Column(Integer, comment="订单状态：0 - 未确认, 1 - 已支付, 3 - 作废, 4 - 退款")