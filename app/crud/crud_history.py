from typing import List, Any
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.history import History
from app.schemas.history import HistoryCreate, HistoryUpdate


class CRUDHistory(CRUDBase[History, HistoryCreate, HistoryUpdate]):
    def get_count_by_owner(self, db: Session, owner_id: int) -> int:
        return db.query(History).filter(History.owner_id==owner_id, History.status==0).count()

    def get_multi_by_owner(self, db: Session, owner_id: int, skip: int, limit: int) -> History:
        return db.query(History)\
            .filter(History.owner_id==owner_id, History.status==0)\
            .order_by(History.id.desc())\
            .offset(skip).limit(limit)\
            .all()

    def create_owner_divination(self, db: Session, history: HistoryCreate) -> Any:
        total = db.query(History).filter(History.owner_id==history.owner_id, History.status==0).count()
        if total >= 100:
            first_history = db.query(History) \
                .filter(History.owner_id==history.owner_id, History.status==0) \
                .order_by(History.id).first()
            if first_history:
                db.query(History).filter(History.id==first_history.id).delete()
        self.create(db, obj_in=history)

history = CRUDHistory(History)
