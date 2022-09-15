from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey,Date,UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Bill(Base):
    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer,  ForeignKey("master.id"))
    master = relationship("Master", backref="master_name", foreign_keys=[master_id])#, foreign_keys=[master_id],uselist=False
    value = Column(Integer,comment="金额，单位'分'")
    bill_date = Column(String,index=True)
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    status = Column(Integer, index=True, comment="状态: 0 - 未支付, 1 - 已支付")
    UniqueConstraint('master_id','bill_date',name="bill_master_id_bill_date_unique")
