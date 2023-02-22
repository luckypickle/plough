from typing import List, Any
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.history import History
from app.schemas.history import HistoryCreate, HistoryUpdate


class CRUDHistory(CRUDBase[History, HistoryCreate, HistoryUpdate]):
    @staticmethod
    def get_count_by_owner(db: Session, owner_id: int) -> int:
        return db.query(History).filter(History.owner_id == owner_id, History.status == 0).count()

    @staticmethod
    def get_index_by_owner(db: Session, owner_id: int) -> int:
        index = db.query(func.max(History.history_index)).filter(History.owner_id == owner_id, History.status == 0).scalar()
        if index is None:
            return 0
        return index

    @staticmethod
    def get_multi_by_owner(db: Session, owner_id: int, skip: int, limit: int) -> History:
        return db.query(History) \
            .filter(History.owner_id == owner_id, History.status == 0) \
            .order_by(History.id.desc()) \
            .offset(skip).limit(limit) \
            .all()

    def create_owner_divination(self, db: Session, history: HistoryCreate) -> History:
        total = db.query(History).filter(History.owner_id == history.owner_id, History.status == 0).count()
        if total >= 100:
            first_history = db.query(History) \
                .filter(History.owner_id == history.owner_id, History.status == 0) \
                .order_by(History.id).first()
            if first_history:
                db.query(History).filter(History.id == first_history.id).delete()
        history = self.create(db, obj_in=history)
        return history

    @staticmethod
    def delete_history(db: Session,history_id:int,owner_id:int) ->bool:
        obj = db.query(History).get(history_id)
        if obj.owner_id == owner_id:
            db.delete(obj)
            db.commit()
            return True
        #super(CRUDHistory,self).remove(db,history_id)
        return False


history = CRUDHistory(History)
