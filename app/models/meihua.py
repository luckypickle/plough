from sqlalchemy import Column, DateTime, Integer, String, func, Text,ForeignKey
from app.db.base_class import Base

class Meihua(Base):
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    cause = Column(String, index=True, comment="起卦原因")
    way = Column(Integer, default=0, index=True, comment="起卦方式 1 - 时间起卦, 2 - 数字起卦")
    shanggua = Column(Integer, index=True, comment="上卦")
    xiagua = Column(Integer, index=True, comment="下卦")
    dongyao = Column(Integer, index=True, comment="动爻")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    pic = Column(Text,default=None,comment="备注")
