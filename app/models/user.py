from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .order import Order  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True, nullable=False)
    full_name = Column(String, index=True)
    wechat = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    orders = relationship("Order", back_populates="owner")
    history = relationship("History", back_populates="owner")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    im_status = Column(Integer,server_default=0)
