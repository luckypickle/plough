from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Reward(Base):
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    order_amount = Column(Integer, comment="金额，单位'分'")
    prev_user_id = Column(Integer, index=True, nullable=False)
    prev_prev_user_id = Column(Integer, index=True, nullable=False)
    prev_amount =Column(Integer, comment="金额，单位'分'")
    prev_prev_amount =Column(Integer, comment="金额，单位'分'")
    order_time = Column(DateTime, index=True, comment="订单时间")