from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class History(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sex = Column(Integer, index=True)
    birthday = Column(String)
    location = Column(String, index=True)
    divination = Column(String)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="history", foreign_keys=[owner_id])
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    status = Column(Integer, index=True, comment="状态: 0 - 显示, 1 - 隐藏")
    isNorth = Column(Boolean, default=True, comment="是否北半球")
    beat_info = Column(String, comment="推算最喜年份信息")
    label_id = Column(Integer)
    history_index = Column(Integer, comment="默认名称自增的index")
    like_str = Column(String, comment="喜")
    dislike_str = Column(String, comment="忌")
    pattern = Column(String, comment="格局")
    top = Column(Integer, server_default='0',comment="是否置顶： 0 不置顶  1 置顶")
    top_time = Column(DateTime, index=True, comment="置顶时间")
