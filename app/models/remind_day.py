from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey,Boolean,Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class RemindDay(Base):
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    title = Column(String, index=True)
    day_time = Column(String)
    name = Column(String, index=True)
    content = Column(Text,default=None,comment="内容")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    remind_days = Column(String, index=True, comment="提醒时间: -1 - 不提醒, 0 - 当天, 1 - 提前一天")
    remind_type = Column(Integer, index=True, comment="提醒方式: 0 - 不重复, 1 - 每年")
    remind_calendar = Column(Integer, index=True, comment="提醒历法: 1 - 公历, 2 - 阴历")
    remind_time = Column(DateTime, index=True, comment="已提醒时间")
