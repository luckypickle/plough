from typing import List, Any
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.master_product import MasterProduct
from app.schemas.master_product import MasterProdcutCreate,MasterProdcutUpdate


class CRUDMasterProduct(CRUDBase[MasterProduct, MasterProdcutCreate, MasterProdcutUpdate]):


    def create_price(self, db: Session, masterProduct: MasterProdcutCreate) -> Any:
        res = db.query(MasterProduct).filter(MasterProduct.master_id == MasterProduct.master_id, MasterProduct.product_id == masterProduct.product_id).first()
        if res is None:
            self.create(db, obj_in=masterProduct)
        else:
            upobj = MasterProdcutUpdate(price = masterProduct.price)
            self.update(db,db_obj=res,obj_in=upobj)
        return True

    @staticmethod
    def delete_master_product_price(db: Session,id:int) ->bool:
        obj = db.query(MasterProduct).get(id)
        db.delete(obj)
        db.commit()
        return True

    @staticmethod
    def get_master_product_price(db:Session,master_id:int):
        res = db.query(MasterProduct).filter(MasterProduct.master_id == master_id).all()
        return res



masterProduct = CRUDMasterProduct(MasterProduct)
