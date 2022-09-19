from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    desc = Column(String)
    status = Column(Integer, nullable=False)
    sort_weight = Column(Integer,default=1,comment="排序权限")
