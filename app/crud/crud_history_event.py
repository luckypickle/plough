from typing import List,Any

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.models.history_event import HistoryEvent
from app.schemas.history_event import HistoryEventCreate, HistoryEventUpdate

class CRUDHistoryEvent(CRUDBase[HistoryEvent, HistoryEventCreate, HistoryEventUpdate]):

    def create_history_event(self, db: Session, historyEvent: HistoryEventCreate) -> Any:
        self.create(db, obj_in=historyEvent)
    
    def get_multi_by_history(
            self, db: Session, *,
            history_id: int,
    ) -> List[HistoryEvent]:
        query = db.query(self.model)
        query = query.filter(HistoryEvent.history_id==history_id)
        return query.order_by(HistoryEvent.create_time.desc()).all()

    @staticmethod
    def delete_history_event(db: Session,id:int,user_id:int) ->bool:
        obj = db.query(HistoryEvent).get(id)
        if obj is not None:
            db.delete(obj)
            db.commit()
            return True
        return False

history_event = CRUDHistoryEvent(HistoryEvent)
