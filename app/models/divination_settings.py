from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class DivinationSettings(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    master_id = Column(Integer, ForeignKey("master.id"))
    entry_type = Column(Integer,default=0, index=True, comment="排盘进入: 0 - 原命盘, 1 - 细盘, 2 - 老师详批")
    show_type = Column(Integer,default=0, index=True, comment="细盘显示: 0 - 流分, 1 - 流时, 2 - 流日, 3 - 流月")
    analysis_isClose = Column(Boolean, default=False, comment="是否关闭命盘解析")
    taimingshen_isClose = Column(Boolean, default=False, comment="是否关闭胎命身")
    xingyun_isClose = Column(Boolean, default=False, comment="是否关闭星运")
    liuri_isClose = Column(Boolean, default=True, comment="是否折叠流日")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")