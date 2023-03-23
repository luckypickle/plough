from typing import List,Any

from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.remind_birthday import RemindBirthday
from app.schemas.remind_birthday import RemindBirthdayCreate, RemindBirthdayUpdate

class CRUDRemindBirthday(CRUDBase[RemindBirthday, RemindBirthdayCreate, RemindBirthdayUpdate]):

    def create_remind_birthday(self, db: Session, remindBirthday: RemindBirthdayCreate) -> Any:
        return self.create(db, obj_in=remindBirthday)
    
    def get_multi_by_owner(
            self, db: Session, *,
            owner_id: int,
            name: str,
    ) -> List[RemindBirthday]:
        query = db.query(self.model)
        query = query.filter(RemindBirthday.owner_id==owner_id,RemindBirthday.name.like("%"+name+"%"))
        return query.order_by(RemindBirthday.create_time.desc()).all()

    @staticmethod
    def delete_remind_birthday(db: Session,id:int,owner_id:int) ->bool:
        obj = db.query(RemindBirthday).get(id)
        if obj is None:
            return False
        if obj.owner_id == owner_id:
            db.delete(obj)
            db.commit()
            return True
        return False

remind_birthday = CRUDRemindBirthday(RemindBirthday)
