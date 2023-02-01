from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class FolderOrder(Base):
    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("folder.id"))
    order_id = Column(Integer, ForeignKey("order.id"))
    master_id = Column(Integer, ForeignKey("master.id"))
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    status = Column(Integer,default=0, index=True, comment="状态: 0 - 显示, 1 - 隐藏")