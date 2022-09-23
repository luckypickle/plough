from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from sqlalchemy import UniqueConstraint


class MasterProduct(Base):
    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer,  ForeignKey("master.id"))
    product_id = Column(Integer,ForeignKey("product.id"))
    price = Column(Integer,comment="产品价格")
    create_time = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    status = Column(Integer,default=1,comment="0 隐藏 1 显示")
    UniqueConstraint('master_id','product_id',name="master_product_master_id_product_id_unique")
