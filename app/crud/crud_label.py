from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import func,or_

from app.crud.base import CRUDBase
from app.models.label import Label
from app.schemas.label import LabelCreate, LabelUpdate


class CRUDLabel(CRUDBase[Label, LabelCreate, LabelUpdate]):
    @staticmethod
    def get_count_by_user_and_name(db: Session, user_id: int, label_name: str) -> Label:
        return db.query(Label) \
            .filter(or_(Label.user_id == user_id,Label.label_type == 0), Label.label_name == label_name) \
            .count()

    @staticmethod
    def get_multi_by_user(db: Session, user_id: int) -> Label:
        return db.query(Label) \
            .all()

    def create_label(self, db: Session, label: LabelCreate) -> Any:
        self.create(db, obj_in=label)

    @staticmethod
    def delete_label(db: Session,label_id:int,user_id:int) ->bool:
        obj = db.query(Label).get(label_id)
        if obj is None:
            return False
        if obj.user_id == user_id:
            db.delete(obj)
            db.commit()
            return True
        #super(CRUDLabel,self).remove(db,history_id)
        return False

label = CRUDLabel(Label)
