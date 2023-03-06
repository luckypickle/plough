from typing import List, Any



from sqlalchemy.orm import Session


from app.crud.base import CRUDBase
from app.models.history_combine import HistoryCombine
from app.schemas.history_combine import HistoryCombineCreate, HistoryCombineUpdate


class CRUDHistoryCombine(CRUDBase[HistoryCombine, HistoryCombineCreate, HistoryCombineUpdate]):



    @staticmethod
    def get_multi_by_owner(db: Session, owner_id: int, skip: int, limit: int) -> HistoryCombine:
        return db.query(HistoryCombine) \
            .filter(HistoryCombine.owner_id == owner_id) \
            .order_by(HistoryCombine.create_time.desc()) \
            .offset(skip).limit(limit) \
            .all()

    @staticmethod
    def delete_history_combine(db: Session,history_combine_id:int,owner_id:int) ->bool:
        obj = db.query(HistoryCombine).get(history_combine_id)
        if obj is None:
            return False
        if obj.owner_id == owner_id:
            db.delete(obj)
            db.commit()
            return True
        #super(CRUDFolder,self).remove(db,history_id)
        return False


history_combine = CRUDHistoryCombine(HistoryCombine)
