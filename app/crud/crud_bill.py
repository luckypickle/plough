from typing import List, Any
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.bill import Bill
from app.schemas.bill import BillCreate, BillUpdate


class CRUDBill(CRUDBase[Bill, BillCreate, BillUpdate]):
    @staticmethod
    def get_all_by_date(db: Session,date:str, skip:int,limit:int) -> (int,List[Bill]):
        sql = db.query(Bill).filter(Bill.bill_date==date)
        return (sql.count(),sql.offset(skip).limit(limit).all())


    @staticmethod
    def create_bill(db: Session,bill:BillCreate):
        pass
    # @staticmethod
    # def get_multi_by_owner(db: Session, owner_id: int, skip: int, limit: int) -> History:
    #     return db.query(History) \
    #         .filter(History.owner_id == owner_id, History.status == 0) \
    #         .order_by(History.id.desc()) \
    #         .offset(skip).limit(limit) \
    #         .all()
    #
    # def create_owner_divination(self, db: Session, history: HistoryCreate) -> Any:
    #     total = db.query(History).filter(History.owner_id == history.owner_id, History.status == 0).count()
    #     if total >= 100:
    #         first_history = db.query(History) \
    #             .filter(History.owner_id == history.owner_id, History.status == 0) \
    #             .order_by(History.id).first()
    #         if first_history:
    #             db.query(History).filter(History.id == first_history.id).delete()
    #     self.create(db, obj_in=history)


bill = CRUDBill(Bill)
