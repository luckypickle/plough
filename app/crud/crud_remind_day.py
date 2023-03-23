from typing import List,Any

from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.remind_day import RemindDay
from app.schemas.remind_day import RemindDayCreate, RemindDayUpdate

class CRUDRemindDay(CRUDBase[RemindDay, RemindDayCreate, RemindDayUpdate]):

    def create_remind_day(self, db: Session, remindDay: RemindDayCreate) -> Any:
        return self.create(db, obj_in=remindDay)
    
    def get_multi_by_owner(
            self, db: Session, *,
            owner_id: int,
            title: str
    ) -> List[RemindDay]:
        query = db.query(self.model)
        query = query.filter(RemindDay.owner_id==owner_id,RemindDay.title.like("%"+title+"%"))
        return query.order_by(RemindDay.create_time.desc()).all()

    @staticmethod
    def delete_remind_day(db: Session,id:int,owner_id:int) ->bool:
        obj = db.query(RemindDay).get(id)
        if obj is None:
            return False
        if obj.owner_id == owner_id:
            db.delete(obj)
            db.commit()
            return True
        return False

remind_day = CRUDRemindDay(RemindDay)