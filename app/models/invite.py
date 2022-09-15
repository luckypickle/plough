from sqlalchemy import Column, ForeignKey,DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Invite(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, index=True, nullable=False)
    phone = Column(String, ForeignKey("user.phone"), unique=True, index=True)
    invite_code = Column(String, comment="邀请码", nullable=False)
    prev_invite = Column(Integer, index=True,default=0)
    prev_prev_invite = Column(Integer, index=True,default=0)
    invite_first_total_reward = Column(Integer, comment="金额，单位'分'",default=0)
    invite_second_total_reward = Column(Integer, comment="金额，单位'分'",default=0)
    payed_reward = Column(Integer, comment="金额，单位'分'",default=0)
    current_level = Column(Integer, comment="等级：0-无,1-青铜,2-白银,3-黄金,4-钻石",default=0)
    order_status = Column(Integer,comment="已注册：1,已下单：2",default=1)
    first_order_time = Column(DateTime, index=True, comment="第一笔下订单时间")
    register_time = Column(DateTime, index=True, comment="注册时间")
