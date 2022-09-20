from sqlalchemy import Column, DateTime, Integer, String, func
from app.db.base_class import Base


class UploadHistory(Base):
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    url = Column(String, index=True)
    status = Column(Integer,default=1)
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")

