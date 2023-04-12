from typing import List,Any

from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.meihua import Meihua
from app.schemas.meihua import MeihuaCreate, MeihuaUpdate

class CRUDMeihua(CRUDBase[Meihua, MeihuaCreate, MeihuaUpdate]):

    def create_meihua(self, db: Session, meihua: MeihuaCreate) -> Any:
        return self.create(db, obj_in=meihua)
    
    def get_multi_by_owner(
            self, db: Session, *,
            owner_id: int,
            skip: int, 
            limit: int
    ) -> List[Meihua]:
        return db.query(Meihua) \
            .filter(Meihua.owner_id == owner_id) \
            .order_by(Meihua.create_time.desc()) \
            .offset(skip).limit(limit) \
            .all()

    @staticmethod
    def delete_meihua(db: Session,id:int,owner_id:int) ->bool:
        obj = db.query(Meihua).get(id)
        if obj is None:
            return False
        if obj.owner_id == owner_id:
            db.delete(obj)
            db.commit()
            return True
        return False

meihua = CRUDMeihua(Meihua)