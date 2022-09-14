from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Withdraw(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    create_user_time = Column(DateTime, server_default=func.now(), index=True, comment="账户创建时间")
    pay_name = Column(String, comment="用户名")
    pay_card_num = Column(String, index=True, nullable=False)
    pay_amount = Column(Integer, index=True, nullable=False)
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    pay_status = Column(Integer, comment="等级：0-未打款,1-已打款,2-拒绝打款")
    phone = Column(String, index=True, nullable=False)