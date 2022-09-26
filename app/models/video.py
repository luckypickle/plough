from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Video(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    top = Column(Integer, server_default='0',comment="是否置顶： 0 不置顶  1 置顶")
    status = Column(Integer, server_default='0')
    video_url = Column(String)
    surface_plot_url = Column(String)
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")

